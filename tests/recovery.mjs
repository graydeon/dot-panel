// SPDX-License-Identifier: AGPL-3.0-only
// Local SQLite rehearsal using repository migrations and synthetic owners only.
// This does not validate Cloudflare D1 export/restore or a deployed code rollback.
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {copyFile, mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const directory = await mkdtemp(join(tmpdir(), 'dot-panel-recovery-'));
const databasePath = join(directory, 'database.sqlite');
const backupPath = join(directory, 'pre-upgrade.sqlite');
let database;
try {
  const journal = JSON.parse(await readFile('drizzle/meta/_journal.json', 'utf8'));
  assert.ok(journal.entries.length >= 7, 'expected published beta migrations');
  assert.equal(new Set(journal.entries.map(entry => entry.tag)).size, journal.entries.length);
  database = new DatabaseSync(databasePath);
  const apply = async entry => {
    const sql = await readFile(`drizzle/${entry.tag}.sql`, 'utf8');
    database.exec('BEGIN');
    try {
      database.exec(sql);
      database.exec('COMMIT');
    } catch (error) {
      database.exec('ROLLBACK');
      throw error;
    }
  };
  await apply(journal.entries[0]);
  const choices = JSON.stringify([{id: 'yes', label: 'Yes'}, {id: 'no', label: 'No'}]);
  const insertQuestion = database.prepare('INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?)');
  insertQuestion.run('synthetic-alice', 'alice-question', 1, 'Synthetic preference?', choices, '2099-01-01');
  insertQuestion.run('synthetic-bob', 'bob-question', 1, 'Synthetic preference?', choices, '2099-01-01');
  database.exec("INSERT INTO answers VALUES ('event-fixture', 'synthetic-alice', 'answered-fixture', 1, 'submission-fixture', 'yes', 'Yes', 'Synthetic preference?', '2026-01-01', NULL)");
  database.exec("INSERT INTO subscriptions VALUES ('subscription-fixture', 'synthetic-alice', 'https://example.invalid/events', 'synthetic-fixture-key', NULL, NULL, NULL, '2099-01-01')");
  database.exec("INSERT INTO deliveries VALUES ('delivery-fixture', 'synthetic-alice', 'event-fixture', 'subscription-fixture', 'pending', 0, '2026-01-01', NULL, NULL, NULL)");
  const baseline = table => JSON.stringify(database.prepare(`SELECT * FROM ${table} ORDER BY owner`).all());
  const tables = ['questions', 'answers', 'subscriptions', 'deliveries'];
  const before = Object.fromEntries(tables.map(table => [table, baseline(table)]));
  database.close(); database = undefined;
  await copyFile(databasePath, backupPath);
  database = new DatabaseSync(databasePath);
  for (const entry of journal.entries.slice(1)) await apply(entry);
  for (const table of tables) assert.equal(baseline(table), before[table], `${table}: upgrade preserves records`);
  assert.equal(database.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
  assert.equal(database.prepare('SELECT count(*) AS total FROM owner_layouts').get().total, 0);
  assert.equal(database.prepare('SELECT count(*) AS total FROM question_queue').get().total, 0);
  assert.throws(() => database.exec("INSERT INTO answers VALUES ('duplicate-fixture', 'synthetic-alice', 'answered-fixture', 1, 'new-submission', 'no', 'No', 'Synthetic preference?', '2026-01-02', NULL)"), /UNIQUE/);
  assert.equal(database.prepare('SELECT id FROM questions WHERE owner = ?').get('synthetic-bob').id, 'bob-question');
  // Demonstrate failed migration rollback rather than continuing with a half-applied schema.
  database.exec('BEGIN');
  try {
    database.exec('CREATE TABLE failed_upgrade_fixture (id TEXT)');
    database.exec('INSERT INTO no_such_table VALUES (1)');
    assert.fail('deliberately broken migration must fail');
  } catch (error) {
    database.exec('ROLLBACK');
    assert.match(error.message, /no such table/);
  }
  assert.equal(database.prepare("SELECT count(*) AS total FROM sqlite_master WHERE name = 'failed_upgrade_fixture'").get().total, 0);
  database.exec("DELETE FROM questions WHERE owner = 'synthetic-alice'");
  database.close(); database = undefined;
  // Whole database restore also restores the earlier schema; pair with its matching code revision.
  await copyFile(backupPath, databasePath);
  database = new DatabaseSync(databasePath);
  for (const table of tables) assert.equal(baseline(table), before[table], `${table}: restore recovers records`);
  assert.equal(database.prepare("SELECT count(*) AS total FROM sqlite_master WHERE name = 'owner_layouts'").get().total, 0);
  assert.equal(database.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
  console.log(`Recovery rehearsal passed: ${journal.entries.length} migrations, two synthetic owners, record/uniqueness preservation, failed-migration rollback and whole-database restore`);
} finally {
  database?.close();
  await rm(directory, {recursive: true, force: true});
}
