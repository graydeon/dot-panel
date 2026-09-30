# Operations, upgrades and recovery

> **Evidence boundary:** automated recovery checks use temporary local SQLite databases and synthetic owners. No production D1 export/restore, hosted rollback, independent-user recovery or private Site change has been performed. Those remain release gates for the user-owned Sites installation.

## Responsibility and deployment boundary

The public repository contains reusable app source. It does not provide a public hosted service, authentication provider or verified ChatGPT catalog install. For the intended framework, each user's dot maintains their own private Sites installation using the supported platform workflow. No central service operator or external auth provider is required. Optional independently hosted deployments retain their own operational responsibilities. The private owner deployment and its personal data are separate.

Keep a release record outside the public repository: code commit, dependency lockfile, applied migration list, deployment/version identifier, configuration revision, backup timestamp/checksum and the operator responsible for recovery. Configuration records must reference secret locations rather than record their values. Database backups can contain owner data and webhook signing secrets; store them encrypted with limited operator access and an explicit retention policy. Never attach them to GitHub or a support issue.

## Automated local rehearsal

Run from the repository root with Node 24:

```sh
npm ci
npm test
node scripts/test-template.mjs
node tests/recovery.mjs
npm run test:runtime
npm run build
```

`tests/recovery.mjs` applies the checked-in migration journal in order to a temporary SQLite database. It seeds two synthetic owners into the original schema, backs up that database, applies later migrations, and checks preservation of questions, answers, subscriptions and the delivery outbox. It also checks answer uniqueness, separate owner records, integrity, rollback of a deliberately failed transaction, and restoration of the original schema and records from the backup. Temporary files are removed when the test ends.

This proves schema/data invariants for the repository SQL on local SQLite. It does **not** prove D1 service behavior, application authorization, automatic queue imports, encrypted backup storage, a network restoration procedure or compatibility of an old deployed Worker with a new schema. Authentication and queue behavior have their own runtime/domain tests. CI runs these checks without credentials or deployment steps.

## Upgrade runbook

1. Record the exact deployed code and applied migrations. Review the new release notes and SQL; never rewrite migrations already applied. Prefer additive changes so the previous Worker can continue reading the upgraded schema.
2. Rehearse the upgrade on an isolated synthetic staging database using the same migration tool and Worker configuration as the intended hosted service. Include two owners, queued questions, a saved answer, pending/accepted deliveries, snapshots and custom layouts. Verify every owner's data remains separate and available after upgrade.
3. Arrange a maintenance window when necessary. Stop new mutations **and delivery workers** using the operator's established maintenance procedure, then take a verified backup and recovery checkpoint. This app does not currently implement a maintenance switch; establish and rehearse that procedure before offering hosted v1 recovery guarantees.
4. Apply only pending migrations to the intended database. Stop immediately on failure; inspect the recorded migration state before retrying. Do not assume the local transaction test establishes D1 migration atomicity.
5. Deploy the reviewed code with its matching configuration. Smoke-test identity, first-use setup, owner isolation, snapshot freshness, layout reload, answering/Dismiss, answer retrieval/acknowledgement and retry handling. Verify anonymous and forged-identity requests still fail closed.
6. Resume writes and delivery only after checks pass. Record results and monitor failures; preserve the pre-upgrade recovery point until the agreed retention period expires.

A backup is verified only after an isolated restore and comparison of schema, migration state, row counts, representative owner records and uniqueness constraints. A checksum alone proves file integrity, not recoverability.

## D1 backup and restore

Cloudflare documents [D1 SQL export/import](https://developers.cloudflare.com/d1/best-practices/import-export-data/) and [Time Travel recovery](https://developers.cloudflare.com/d1/reference/time-travel/). Select a supported recovery method appropriate to the operator's account and retention needs. A Worker rollback does not restore database contents.

The following are **operator examples**, not commands executed by this project. `DB` must resolve to the operator's intended database; confirm the target first. Use an operator-controlled backup path outside the repository:

```sh
npx wrangler d1 export DB --remote --output=/operator-backups/dot-panel.sql
```

Rehearse import only into an isolated, empty restore target. Importing into the live database can collide with existing tables or records; do not use SQL import as an in-place reset:

```sh
npx wrangler d1 execute RESTORE_TARGET --remote --file=/operator-backups/dot-panel.sql
```

Neither command is part of CI. Creating or rebinding a restore target is an infrastructure action requiring the operator's authority. Keep the old target and restore evidence until recovery is verified. Native Time Travel procedures and retention are governed by the platform; verify current account capabilities before relying on them.

## Rollback and delivery reconciliation

For an application-only failure with a backward-compatible schema, select the previously verified Worker version using [Cloudflare's rollback procedure](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/). Check bindings/configuration and data compatibility before resuming traffic. Do not blindly reverse SQL migrations or delete user tables.

If data/schema recovery is necessary, stop mutations and deliveries, preserve the failing state for restricted investigation, restore the reviewed recovery point to an isolated target, pair it with matching code/configuration, run the smoke checks above, and switch targets only after operator approval. Document the time window of potential lost writes; do not promise zero data loss.

A database restore may bring back delivery rows whose webhook already reached a receiver. Delivery event IDs remain stable and consumers must deduplicate them. Before resuming, reconcile externally received events and acknowledgements against the restored outbox; avoid reperforming a consequential action merely because an acknowledgement was lost. A Dot Panel choice is an ordinary answer and cannot authorize actions that require a platform confirmation.

## Required private Sites recovery evidence before v1

| Gate | Required evidence | Current proof |
| --- | --- | --- |
| Upgrade | Representative staged data survives real D1 migration; owners stay isolated | Synthetic SQLite rehearsal only |
| Backup/restore | Protected backup restored to isolated D1 target; data and migration state compared | Local whole-database file restore only |
| Rollback | Previous code/config works with the chosen recovery schema; smoke checks pass | Runbook; no hosted rollback |
| Delivery reconciliation | Stable event IDs suppress duplicates after restore; receiver acknowledgements reconciled | Domain retries/idempotency tests; no external recovery rehearsal |
| Operator readiness | Named responder, monitoring, maintenance procedure, retention and incident contacts | Not established by repository CI |

Publish only sanitized summaries of these results. Share affected users' data through authorized private support channels when necessary. Follow [SECURITY.md](../SECURITY.md) for vulnerability reporting.
