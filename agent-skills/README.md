# Dot Panel widget authoring bundle

Two source-editing agent skills and one small starter for workflow-specific widgets. This bundle is distributed with Dot Panel source under **AGPL-3.0-only**; retain the release's `LICENSE` and asset/third-party notices. It contains no artwork, credentials, private owner data, runtime loader, or hosted service. It is not automatically installed as a personal skill.

Keep this directory intact so the skills' relative links resolve. Ask a coding agent to read `create-dot-panel-widget/SKILL.md` or `edit-dot-panel-widget/SKILL.md` and work in your authorized source checkout. Example: “Use the create skill to add a release-checklist card using my already-connected project tracker; show the last verified summary and source time.” The agent must verify source access and data-sharing permission before saving real information.

## Implemented extension points

The layout-enabled public checkout uses these ordinary TypeScript/React interfaces:

- `lib/panel-config.ts`: `PanelModule` selects `project`, `briefing`, `calendar`, or `links`, with stable `id`, `title`, `placement`, `enabled`, `source_type`, optional `source_reference`, `mode`, optional `snapshot_key`, and `links`. Configuration allows at most 12 modules and six HTTPS links per module; it is not an integration grant. Config writes require owner review and `expected_version`.
- `lib/layout-model.ts`: `widgetRegistry(config, projects)` returns `Widget` objects with `id`, `title`, `kind`, and optional `module`. Built-ins use `needs-you`, `usage`, `calendar-today`, and `calendar-week`; configured cards use `module:<module.id>`. The kind union is `needs | today | week | usage | project | briefing | links`. There is no registration function or downloadable plugin manifest.
- Layout `Rect` is `{id,page,x,y,w,h,hidden?}` in a 12×12 grid, bounded to 16 pages. `Layouts` is `{schema_version:1,portrait:Rect[],landscape:Rect[]}`. `minimum`, `defaultRects`, `validateRects`, and `reconcileLayouts` own sizing, defaults, validation, and compatibility. Preserve valid saved rectangles instead of resetting them.
- `src/Panel.tsx`: its `renderWidget(widget)` callback is passed to `src/widget-board.tsx`. New renderers are statically imported and dispatched here. In the hosted source variant these files are `app/touch.tsx` and `app/widget-board.tsx`; do not copy its hosting helpers into a public export.
- `lib/layout-store.ts`: owner-scoped layout persistence guards both `expected_version` and `expected_module_version`; `GET/POST /api/layout` uses authenticated owner identity. No widget should invent a caller-supplied owner ID or weaken authentication.

If the checkout lacks `layout-model.ts` or `widget-board.tsx`, it predates this layout framework. Update the source release first; these files are prerequisites, not APIs supplied by this bundle.

## Starter integration

The starter reuses an existing project module and overview snapshot. It does not require a new enum value, database table, migration, or registry engine.

1. Copy `template/` into `src/widgets/workflow-snapshot/` in a working source checkout. Rename its display text, stable ID, and snapshot key for the requested workflow before first use. Keep `kind:'project'` unless a new kind is genuinely necessary. `manifest.ts` is a typed config entry, not an automatically loaded manifest.
2. For the standard card, no renderer change is necessary: an owner-reviewed module entry makes `widgetRegistry` create the card. Read current config and append/merge the entry through `update_panel_config`; never submit just this entry over an existing array. Retain all unrelated modules and use the current version. Saving a source reference does not fetch it.
3. For custom presentation, statically import `SnapshotWidget` and `workflowModule` into the panel. Before its generic module branch, dispatch when `widget.id === 'module:' + workflowModule.id`, passing `widget`, `projects`, `nowMs: Date.now()`, a workflow-appropriate `staleAfterMs`, and an `onOpen(trigger)` callback that opens existing accessible details for this module. Keep the trigger for focus restoration. The component has no side effects or fetching. It deliberately leaves all source links to that detail view; preserve access to every configured link there. Reuse `.module-widget`, `.tile`, `.module-details`, and theme tokens.
4. Use the existing registry result and saved-layout reconciliation. Do not insert a duplicate hard-coded widget or reset the owner's layout. For new kinds, deliberately extend the config schema/validation, registry union, `minimum`, defaults, renderer, and tests together; no arbitrary-code runtime is provided.

## Data and adapter contract

The example reads `overview.projects`: `{name,update,source_timestamp,source_url?}`. Match `name` to `module.snapshot_key ?? module.title`. The backend's `update_touch_overview` tool accepts a summary (400 characters), source timestamp, `expected_updated_at`, and at most five projects (names 80 characters, updates 240). Read `get_touch_status` first and preserve unrelated projects and summary. The five-project snapshot limit is independent of the 12-module config limit; do not discard other projects to fit a new widget. If the workflow needs more capacity or structured records, implement and test a separately scoped owner-bound snapshot store instead.

Adapter flow: authorized native source read → minimal validated summary with genuine source time → owner-authorized snapshot write → read-only widget. Neither the browser nor this template calls source services. Existing calendar and usage snapshots have their own tools and schemas; inspect those rather than forcing them through projects. Calendar is read-only. Do not change fixed credentials, hosted auth, owner identity, or webhook signing to connect a widget.

Use source timestamps for evidence age; retrieval time is not proof that source content changed. `snapshotView` explicitly reports fresh/stale/missing/invalid/link-only and takes an injected clock and freshness budget. On source failure preserve the last verified snapshot and show its age; never write a fabricated successful update. A genuine disconnected/error state needs explicit validated metadata if the existing snapshot contract cannot represent it. The starter has no scheduling, refresh worker, arbitrary JSON store, or automatic OAuth integration.

## Verify before delivery

After copying the template into the checkout, run its small pure-model test with the existing esbuild dependency (no install required):

```sh
node --input-type=module -e "import {build} from 'esbuild'; await build({entryPoints:['src/widgets/workflow-snapshot/snapshot-model.test.ts'],bundle:true,platform:'node',format:'esm',outfile:'/tmp/dot-panel-snapshot-test.mjs'})"
node /tmp/dot-panel-snapshot-test.mjs
npm test
npm run test:runtime
npm run build
```

The starter test covers eight freshness/matching cases; it is not an end-to-end integration test. Add widget-specific owner isolation, conflict handling, backward-compatible config/layout, and rendering checks. In a browser verify minimum/large sizes, portrait/landscape, light/dark, touch/keyboard, focus recovery, accessible overflow/details, long text, empty and stale states, and no document scrolling. New migrations must preserve existing data and be tested on a synthetic old database. Run production migrations or publication only when separately authorized. Include changed source, synthetic tests, skills, and updated release manifest in the authorized export; exclude private fixtures, URLs, credentials, database state, build artifacts, and installed dependencies.
