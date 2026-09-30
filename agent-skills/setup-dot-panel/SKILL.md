---
name: setup-dot-panel
description: Install the free AGPL Dot Panel framework into the requesting user's own private ChatGPT Site and guide its managed-identity MCP connection, reviewed modules and harmless answer verification. Use for first setup or resuming an interrupted installation; requires available Sites capabilities and a compatible source checkout, not a shared hosted service.
---

# Set up a private Dot Panel

Dot Panel is source plus agent skills. Each user owns a private Site and its platform-managed identity/plugin connection. Installing this skill does not provision a Site, connect accounts, subscribe to events or start refreshes. Do not request custom tokens, publish a personal Site, configure a shared service, or reuse another user's endpoint.

## Check prerequisites before creating anything

1. Confirm the user requested installation, the intended personal/workspace ownership, and whether an interrupted installation already has a retained Site ID/source checkout. Inspect only that installation. Reuse its Site or registration attempt; resolve uncertain creation results before retrying. Similar unrelated Sites are not installation candidates.
2. Load the installed Sites building, hosting and MCP skills, plus their selected execution-profile setup and registration references. Discover callable native Sites tools and use their current schemas. If absent/disconnected, report the missing Sites capability and ask the user to enable the supported Sites workflow. Do not invent an app dependency ID, installation link or credential workaround. A canonical dependency lookup has not been established.
3. Confirm a trusted released or explicitly reviewed candidate Dot Panel source checkout, its version/hash, AGPL-3.0-only LICENSE, notices, package lock and original assets. Retain sanitized reusable source separately from private deployment state. Do not copy another user's private hosted repository, snapshots, database, layout, links, credentials or hosting IDs. Keep the per-installation checkout and identity local/private; never commit them to the public framework.
4. Check the source's actual Sites compatibility. The portable public Worker currently uses a trusted `AUTHENTICATOR` binding and strips caller identity headers; adding `.openai/hosting.json` does not implement Sites identity. Require a reviewed compatible Sites entrypoint/adapter that uses platform identity only behind the managed hosting boundary, enforces authenticated owner isolation, and preserves API/MCP/schema behavior. If missing, stop before provisioning/deployment and report this implementation prerequisite. Do not weaken portable authentication or treat arbitrary request headers as identity.

## Select the Sites build

Use `worker/sites.ts` with `npm run build:sites`; it emits `dist/client` and `dist/server/index.js`. Do not publish the optional standalone `worker/index.ts` entrypoint to Sites. If the current native build helper invokes `scripts.build`, select `node scripts/build-sites.mjs` in this new installation checkout. Add the returned actual Site ID, logical `DB` binding and `mcp` capability using current Sites schema; do not copy a personal manifest or add static-only mode. The new entrypoint has synthetic isolation checks, but live hosting identity and build compatibility still require verification.

## Create once, keep private, retain recovery context

Use the capability workflow: Dot Panel needs persisted data and MCP. Run installed Sites setup helpers in the installation checkout with the correct execution profile. Request only required logical database/MCP capabilities; add `mcp` while preserving existing capabilities. New registration uses native `create_site` once and starts private/unpublished. Enable workspace plugins only after actual eligibility discovery confirms each requested source is allowed and the user authorizes it.

Retain the returned Site ID in the installation's private manifest through the registration helper. Keep temporary source credentials in session memory/stdin using the Sites workflow; never write or display them. On resume, `get_site` the exact retained ID and open its source with the supported workflow. Do not register a replacement because one connection or deployment failed.

Run relevant app, identity/isolation, migration/recovery and build checks. Use the installed Sites save/private-deploy sequence and literal returned IDs, without changing audience or broadening permissions. A successful native deployment result is deployment evidence, not complete user setup. Record version/commit and the exact returned private URL in private handoff context, not public examples. If runtime approval is required, respect it; an ordinary panel answer cannot replace it.

## Connect the provisioned private plugin

Call native `get_site` with `include_mcp_connection: true` for the user's exact retained Site. Use only its returned plugin ID with the supported plugin-management `suggest_plugins` installation UI. Sites provisions the App/private plugin and manages OAuth: reuse it; do not create a separate App/plugin, use local MCP configuration or run MCP login commands.

If the plugin is already installed or that UI is unavailable, direct the user to **Plugins → Personal → Created by you**, open their Site plugin, and choose Install/Connect. A click/authentication may require the user. Do not report a connection until a harmless read-only call to that specific installed plugin succeeds. Prefer actual `get_panel_setup_status`, `get_panel_config` or `get_touch_status` discovered from its tools. Distinguish missing tools, denied identity and empty user data.

## Configure and verify

Follow [the setup protocol](../../docs/agent-setup-protocol.md). Confirm the user's assistant name, desired modules, timezone and what the idle screen reveals; preserve initialized configuration and both layouts. Present a compact proposed configuration, write only reviewed fields with current version guards, and read back. Configuration is not a connector grant.

Sources are optional. Read a selected source only through an available already-authorized integration/helper, then save a minimal timestamped snapshot through discovered tools. Clearly distinguish snapshot/manual/link-only from actual scheduled refresh. A missing feed is unavailable, not live, unlimited or empty by inference. Personal usage helpers are not universal integrations; do not copy the original owner's process or state.

For answer delivery, discover supported event sources and the exact installed plugin's current webhook schema. Only after explicit user authorization, configure a supported `answer.submitted` subscription for the intended conversation/dot. Preserve existing triggers; do not create duplicates, broaden scope or substitute polling when a webhook is requested. For future ordinary answers, omit the optional `question_id` filter: scope remains this authenticated owner. For a deliberately question-filtered test, enqueue/read back the question first, subscribe second, verify connection, and answer last. No pre-subscription answer replay is provided. Reconcile uncertain task-service saves before retrying; missing Site connection alone is not task-service dedup evidence. If event support is absent, report the missing callback path and keep setup incomplete.

With the user's awareness, enqueue one uniquely identified harmless preference test (yes/no or ordinary multi-choice). Verify the actual panel interaction, correlated event ID, intended owner/conversation, saved answer and subsequent acknowledgement after responding. Dismiss cancels without an answer/webhook; Later leaves pending. A simulated call is not a human screen tap. Never use the panel to approve purchases, grants, secrets or other consequential actions; retain required platform confirmation.

## Handoff truthfully

Report separately: private deployment, plugin connection/read-only call, reviewed configuration, each feed's observation/refresh status, subscription and actual answer delivery, and device checks. Say which external tests were not run. Save enough private recovery context to resume the same installation, with no credentials. Do not call installation complete while managed-runtime identity compatibility or the promised event path is unverified. See [framework installation](../../docs/framework-installation.md).
