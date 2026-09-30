// SPDX-License-Identifier: AGPL-3.0-only
import {build} from 'esbuild';
import {mkdtemp, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';

const directory = await mkdtemp(join(tmpdir(), 'dot-panel-template-'));
try {
  const result = await build({
    entryPoints: ['agent-skills/template/snapshot-model.test.ts'],
    bundle: true, platform: 'node', format: 'esm', write: false,
  });
  const file = join(directory, 'template.mjs');
  await writeFile(file, result.outputFiles[0].text);
  const run = spawnSync(process.execPath, [file], {stdio: 'inherit'});
  if (run.error) throw run.error;
  process.exitCode = run.status ?? 1;
} finally {
  await rm(directory, {recursive: true, force: true});
}
