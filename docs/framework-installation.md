# Install and maintain your own private Dot Panel

Dot Panel is a free **AGPL-3.0-only framework with agent skills**, not a shared hosted dashboard. Your dot uses supported Sites tooling to create and maintain your own private Site, with platform-managed sign-in and that Site's private MCP plugin. Retain LICENSE and notices with source. Sites plan availability/usage limits still apply; free source does not promise unlimited platform hosting. [Sites documentation](https://learn.chatgpt.com/docs/sites).

The public framework distribution and your private runtime connection are separate. Installing a framework skill does not create a Site, connect accounts, subscribe to answers or refresh feeds. There is no universal Dot Panel MCP endpoint or credential to paste. A source tarball is not an installable plugin ZIP. No submission package is currently provided; verify the code and setup flow before preparing one.

## Ask your dot to set up the framework

Use [setup-dot-panel](../agent-skills/setup-dot-panel/SKILL.md) in an authorized source checkout. The dot checks:

1. Sites tools/skills are available for your account and the chosen ownership context.
2. Retained source is the trusted sanitized release, with license, lockfile and original assets intact.
3. The source has a verified Sites-compatible entrypoint and owner-isolated data handling.
4. No retained installation or uncertain creation attempt needs resuming.

`worker/sites.ts` is the dedicated managed-auth entrypoint; `npm run build:sites` emits `dist/client` and `dist/server/index.js`. Its shared routes have synthetic Sites identity/isolation tests. **Live Sites build/deploy and boundary verification remain outstanding.** The optional standalone Worker uses a separate `AUTHENTICATOR` interface and is not the Sites entrypoint. Before native publishing, the Site-owning agent sets the retained checkout's build script to `node scripts/build-sites.mjs`, creates the hosting manifest with the actual returned Site ID, logical `DB` binding and `mcp` capability, and uses the supported Sites helpers. Do not bypass authentication or deploy a local fixture to make setup succeed.

Once those prerequisites pass, the dot creates one private Site using supported helpers, retains its identity privately, runs checks, and deploys privately. It requests that Site's connection through `get_site` with `include_mcp_connection: true`, then offers the supported installation UI using the returned plugin ID. If the UI is unavailable, open **Plugins → Personal → Created by you**, select your Site plugin and choose Install/Connect. Complete the platform connection steps yourself when required; the dot verifies a harmless read-only tool call afterward.

Managed Sites authentication, trusted identity headers and reuse of its provisioned private plugin follow the installed Sites MCP workflow. They do not justify trusting arbitrary headers on a publicly exposed Worker or publishing your private runtime as a catalog service.

## Finish guided setup

Review the assistant name, modules, timezone and visible detail. Existing layouts/configuration are preserved. Each selected feed needs an available authorized source or helper and must state whether it is a snapshot, manual update or verified scheduled refresh. Calendar/project/usage sources are not silently built in. A personal usage helper does not become universal through skill installation.

If you want answers delivered back to your dot, explicitly authorize the supported answer event subscription. The dot discovers the exact installed plugin's event schema and preserves existing subscriptions. Run a harmless preference test through the actual panel and verify its correlated answer in the intended conversation. Dismiss cancels; Later leaves a question pending. Ordinary yes/no and multiple-choice answers do not approve consequential actions or bypass platform confirmation.

One-time connections do not execute themselves. Schedules and unattended updates need separately authorized, supported setup and real verification. Unsupported sources can remain clearly labeled manual/link-only; a promised required callback or authentication path cannot be marked complete while blocked. Follow the [setup protocol](agent-setup-protocol.md).

## Maintain and recover

Use [maintain-dot-panel](../agent-skills/maintain-dot-panel/SKILL.md) for updates and repair of the same private installation. Retain private source/deployment context, verify backup and rollback compatibility before risky migrations, and preserve layouts, data, connections and triggers. The [operations guide](operations.md) describes current recovery checks. Source updates must not silently replace personal state or publish it to GitHub.

## Verification still required

These instructions are an executable agent contract, not evidence that a fresh account completed installation. Release evidence must include a supported retained-source-to-Sites adapter/build, independent first-user creation and connection, actual answer subscription/delivery, per-owner authorization and recovery. Device and accessibility testing must distinguish browser automation from a real iPad/VoiceOver session. A discoverable public framework skill still requires its own supported distribution/review; no canonical Sites package dependency was resolved, so prerequisites are explicit rather than invented.

Future packaging should use the documented root `plugin.json`, `skills/` and optional `mcp.json`/assets structure. Framework skills must not embed the original owner's private endpoint, hosted App ID or secrets. Public tool requirements apply if a public MCP service is ever included; this framework design does not provide one. [Package documentation](https://developers.openai.com/plugins/build/plugins), [submission documentation](https://developers.openai.com/plugins/deploy/submission).

## Optional automatic usage snapshots

The retained framework includes `scripts/usage-tracker.py` and the [usage management skill](../agent-skills/manage-dot-panel-usage/SKILL.md). Offer it only when the owner wants local automatic usage snapshots and has a compatible existing Codex CLI connection. Follow the [local tracker guide](usage-tracker.md), verify the selected private panel, and perform a one-time read/write before any authorized background launch. Skill installation alone starts no process. No additional authentication service or developer-operated host is required; unavailable CLI support leaves this optional module manual/unavailable.
