---
name: maintain-dot-panel
description: Maintain or upgrade the requesting user's existing private Dot Panel Site using retained source, platform-managed identity and verified configuration, while preserving data, layouts and event subscriptions. Use for an authorized update, refresh repair or recovery, not installing a replacement Site or changing access.
---

# Maintain an existing private Dot Panel

Use the user's exact retained Site ID and installation checkout. Do not search unrelated projects or reuse another owner's endpoint. If identity/context is missing, ask for the selected installation before mutations. Load current Sites hosting/MCP skills and schemas; use `get_site` and the normal source-opening workflow. No new registration, App, OAuth flow or credential generation is needed for ordinary maintenance.

## Read and plan before writes

- Confirm requested scope, current source/deployed version, private audience and owner. Inspect read-only configuration, both layouts, setup/feed status and existing event/schedule context. Read access does not authorize new sources or recurring work.
- Fetch only the trusted sanitized framework release into a separate source checkout; inspect license/notices and changes. Preserve newer installation-specific code; reconcile conflicts explicitly. Never overwrite the private manifest, secrets, snapshots, database or newer public docs with an old archive.
- Review migrations and [recovery guidance](../../docs/operations.md). Make a verified private backup using available authorized storage/database operations before risky schema updates, without exporting personal data to public artifacts. Prove restore/rollback compatibility on synthetic data; a saved code version alone is not a database backup. If safe backup/recovery is unavailable, report that blocker before a destructive update.

## Apply the smallest authorized change

Use supported Sites helpers and save/private-deploy workflow. Preserve project identity, audience, managed OAuth, logical bindings and connector declarations. Do not trust spoofed identity headers or turn on local fixtures in hosted code. Keep temporary workflow credentials in memory/stdin and out of files, logs and public source.

Run relevant tests/builds and migration/recovery checks. Reuse successful results only for unchanged inputs. Record the actual saved/deployed version and previous recovery point privately. If a deployment outcome is uncertain, inspect that same deployment ID; do not duplicate publication or create another Site. No public framework tag/release or permission changes are implied by maintaining a private installation.

## Verify and repair without resetting

Read-only verification must target the installed private plugin for this Site. Reconnect through the returned plugin ID/UI if needed; fallback is **Plugins → Personal → Created by you**. No separate local MCP setup or invented dependency ID.

Compare configuration and both saved layouts before/after. On version conflicts, reread and reconcile rather than force overwriting. Verify owner isolation and truthful missing/stale/error feed states. Refresh only requested sources through available authorized connections/helper actions; a one-time connection is not a running updater. Keep personal usage helpers optional and user-specific.

Preserve webhook triggers and enabled/paused schedules. Retry only through actual supported delivery operations; inspect the exact saved event and acknowledgement before handling it again. Reuse idempotency IDs after uncertain writes. Dismiss/answer races must resolve once; cancellation must not manufacture an answer. Ordinary preferences never replace required platform approvals.

Run a harmless real answer test only when needed and authorized, label simulated versus actual delivery, and acknowledge after responding in the intended conversation. If rollback is needed, use the documented compatible version plus appropriate data recovery; do not restore old data over newer owner changes without explicit authorization.

Return what changed, verification evidence, retained recovery point and remaining failures. A successful deploy or passing unit tests alone does not prove independent-user setup, iPad/VoiceOver or live callback delivery. See [framework installation](../../docs/framework-installation.md).
