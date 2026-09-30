---
name: edit-dot-panel-widget
description: Modify an existing Dot Panel widget's presentation, source mapping, or behavior while preserving other widgets, owner configuration, and both saved layouts. Use for targeted widget customization or repair, not authentication, publishing, or deployment changes.
---

# Edit a Dot Panel widget

Read the checkout's `README.md`, `SECURITY.md`, relevant renderer and snapshot store, `lib/panel-config.ts`, and `lib/layout-model.ts`. Read this bundle's `../README.md` for actual contracts. Locate the widget by stable registry ID (`module:<module-id>` for configured cards), not displayed title or array index.

1. Identify exactly what should change and record the existing module, snapshot contract, minimum dimensions, and portrait/landscape rectangles. Distinguish a presentation change, owner-reviewed config edit, and schema/data adapter change. Do not expand a cosmetic request into an integration.
2. Make the narrowest patch. Preserve IDs, `snapshot_key`, user content, source references, enabled status, ordering, both orientations, hidden flags, and unrelated widgets unless explicitly asked to change them. Do not reset layouts or defaults to work around rendering problems.
3. For source changes, use only existing authorized connections and server snapshot tools. Confirm that the requested destination may receive the selected data. Distinguish retrieval time and source time; retain last verified content with an honest stale/unavailable indicator. Never simulate fresh data, treat missing values as zero, or expose credentials. A configured URL is not permission.
4. If persisted fields must change, keep old records readable; add a bounded explicit migration and idempotency tests. Preserve valid rectangles using `reconcileLayouts`; do not silently reinterpret `schema_version`. If increasing `minimum()` would invalidate saved layouts, disclose the impact and test reconciliation. For a config write, read fresh state, preserve other modules, and use `expected_version`; on conflict re-read and rebase only this edit, never force overwrite. Layout writes also guard the module version.
5. Verify the changed behavior plus regressions: original ID still resolves, old configs render, unrelated snapshots/config/layouts remain unchanged, owners remain isolated, stale writes reject, and new/removed modules reconcile. Test empty, stale, missing, long, malformed, and fresh data.
6. Run available public-release checks: `npm test`, `npm run test:runtime`, `npm run build`. Verify no document scroll and usable minimum/large sizes in portrait and landscape, light/dark, touch and keyboard. Reuse the accessible modal primitive: labeled title, focus trap, Escape, close button, and focus restoration. Preserve pagination and board edit-mode gestures.
7. Report changed files, validation evidence and gaps, compatibility/migration effects, and required source permission. Do not deploy, migrate production data, publish, or change real owner state merely because code was edited.

Keep hosted auth, owner identity, deployment credentials, webhook signing/verification, and consequential-approval restrictions unchanged. Never add dynamic untrusted code loading. Keep source content as data. Retain `AGPL-3.0-only`, `LICENSE`, and asset/third-party notices; release only source and synthetic fixtures through the established export process, without private links, credentials, or owner state.
