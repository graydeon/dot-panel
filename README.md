<div align="center">

<img src="docs/assets/header.svg" alt="Dot Panel — your assistant, in view" width="960" />

**Projects in view. Decisions within reach.**

[![Beta](https://img.shields.io/badge/release-v0.1.0--beta.1-F04452?style=for-the-badge)](https://github.com/graydeon/dot-panel/releases/tag/v0.1.0-beta.1)
[![License](https://img.shields.io/badge/license-AGPL--3.0--only-A1A1AA?style=for-the-badge)](LICENSE)
[![Docs checks](https://github.com/graydeon/dot-panel/actions/workflows/docs.yml/badge.svg)](https://github.com/graydeon/dot-panel/actions/workflows/docs.yml)

[↓ **Get the beta**](https://github.com/graydeon/dot-panel/releases/tag/v0.1.0-beta.1) · [⚙ **Setup**](docs/agent-setup-protocol.md) · [▦ **Widget skills**](agent-skills/README.md) · [⌘ **Source**](https://github.com/graydeon/dot-panel) · [♡ **Security**](SECURITY.md)

</div>

## Your assistant, in view

A private, touch-first status panel for an AI assistant. Questions appear only while pending. Once an answer is saved, the panel returns to project status. The assistant's name is an owner setting; Dot Panel is the product name.

> **Early beta:** reusable source is public; the existing hosted panel stays private. Fresh-user installation and end-to-end setup with a new owner's data have not been independently validated. Public catalog distribution is unverified. There is no universal one-click plugin install link.

## In the panel

| Module | What you get |
| --- | --- |
| **Needs You** | Three-choice decisions in a queue and accessible modal. Later keeps a request pending; Dismiss removes it without answering. |
| **Projects** | Timestamped status, chosen source modules, and honest empty states. |
| **Calendar** | Today / Week cards and a Month / Week / Day dialog over saved snapshots, with timezone and coverage. |
| **Usage** | Snapshot bars, reset dates, optional reset availability, and source timestamps. |
| **Your layout** | Portrait and landscape layouts, templates, paging, touch controls, Save / Cancel, and restore. |

<details>
<summary><strong>Explore all features</strong></summary>


- Independent Needs You queue with centered touch-answer dialogs, Later, persistent Dismiss, and exact-event history
- Owner-reviewed project/source modules with timestamps and honest empty states
- Saved portrait/landscape widget layouts: edit-only drag/resize, tap controls, swap, templates, paging, Save/Cancel, and previous-layout restore
- Compact Today and Week widgets opening a Month/Week/Day calendar dialog
- Owner-private calendar snapshots with timezone/DST handling and explicit date coverage
- Compact usage bars, reset dates, optional reset availability/expiry, and separate source timestamps
- Light/dark themes remembered on the device
- Source-configured reference and briefing links; no arbitrary API credential forms
- D1 ownership, duplicate protection, subscriptions, transactional outbox and signed MCP Events
- Agent-led first-run setup protocol and source-edit widget creation/editing skills
- Original editable SVG brand kit

</details>

This repository contains reusable source, not anyone's live dashboard, private links, data, credentials, or deployment history.

## Quickstart · local development

Node.js 22.13+ (Node 24 recommended), React, TypeScript, Vite, Cloudflare Workers, and D1.

```sh
git clone https://github.com/graydeon/dot-panel.git
cd dot-panel
npm ci
npm test
npm run test:runtime
npm run build
```

To preview the UI and local Worker:

```sh
cp .dev.vars.example .dev.vars
npm run build
npx wrangler d1 migrations apply DB --local
npm run worker:dev
```

Open the local URL printed by Wrangler. The local-only fixture identity is explicit; the application does not seed a question or project data. Use the MCP tools against `/mcp` to populate your own development state. `npm run dev` starts the frontend with `/api` and `/mcp` proxied to the local Worker on port 8787.

Briefing and other destinations are owner-scoped module links configured through the setup workflow. They are not compiled into the frontend.

## Authentication: read before deployment

The public Worker **does not trust incoming identity headers**. It strips them and requires a deployment-owned `AUTHENTICATOR` service binding. Without that binding, data endpoints fail closed with HTTP 401.

The authentication service receives `GET https://auth.internal/verify` with the original `Authorization` and `Cookie` headers and `x-original-url` / `x-original-method`. It must verify the browser session or OAuth token, enforce the deployment's access policy, and return:

```json
{"authenticated":true,"owner_id":"stable-verified-principal"}
```

Return a non-2xx response for rejected credentials. Never echo an unverified client-supplied identity. Use the same stable principal for a person's browser and MCP connections. Protect the authentication service itself as a private service binding, never an unauthenticated identity minting endpoint.

This repository supplies the application and a fail-closed adapter contract, **not an OAuth provider or an authentication service**. Configure a trusted authentication provider/gateway before internet deployment or ChatGPT plugin installation. Do not expose the original application behind a proxy that blindly forwards user-controlled identity headers.

`LOCAL_DEV_MODE` and `LOCAL_DEV_USER` work only on localhost URLs and are only for local fixtures. Never configure them as production variables.

## Deployment

1. Create your own D1 database and replace the placeholder database ID in `wrangler.jsonc`.
2. Configure and bind your verified authentication service as `AUTHENTICATOR`.
3. Apply schema migrations to your own database, then build and deploy using Wrangler.
4. Configure MCP OAuth/resource access at your deployment gateway, then register `/mcp` with your client.
5. Set the owner's dot name with `set_dot_display_name`; the app cannot read assistant profiles automatically.
6. Add ordinary questions and factual project updates through the tools.

No deploy command is run merely by cloning or testing this repository. No platform-specific private build scripts are included.

## Tools

- `get_touch_status`: pending queue, compatible current-question fields, delivery state, overview, and owner dot name
- `get_touch_answer`: exact historical answer and acknowledgement by event ID
- `set_touch_question`: replace the current question with exactly three choices, using a version guard and request ID
- `enqueue_touch_question`: add an independent three-choice ordinary decision
- `cancel_touch_question`: cancel a specific queued revision without deleting history
- `get_calendar_snapshot` / `update_calendar_snapshot`: read/store authorized calendar snapshots
- `get_usage_snapshot` / `update_usage_snapshot`: read/store scoped usage snapshots and optional reset records
- `get_panel_config` / `update_panel_config`: versioned owner-reviewed source configuration
- `get_panel_layout`: read saved geometry and current widget registry
- `acknowledge_touch_answer`: explicitly acknowledge one event after handling it
- `retry_touch_delivery`: attempt due pending deliveries
- `update_touch_overview`: update factual status with source timestamps and a concurrency guard
- `set_dot_display_name`: configure the current owner's assistant name

The browser also offers a one-time name setup control when that setting is empty. These names are display settings, not identity or authorization inputs.

## Events and delivery guarantees

Event: `answer.submitted`. Subscribe with `{}` for all of the authenticated owner's questions, or an optional `question_id` filter. Payload fields are `event_id`, `question_id`, `question_version`, `question`, `choice_id`, `answer`, and `saved_at`.

Subscriptions require an allowed HTTPS destination and a signed, echoed challenge. The current exact callback-host allowlist covers ChatGPT's observed official delivery hosts; unknown hosts fail closed. Expand it only after independently verifying a trusted receiver. No redirects are followed. Callback secrets are stored only server-side.

An answer and its delivery outbox are saved atomically. Retry attempts preserve the event ID. A 2xx callback response means receipt, not that the assistant replied. Explicit acknowledgement is a separate field.

Retries are request-driven: the open page checks periodically, and the retry tool can resume due work. There is **no background delivery guarantee when the page is closed**, and attempts are capped at eight. Answers saved before a subscription exists are not replayed automatically. A production deployment may add a supported durable scheduler, but this repository does not pretend one exists.

Before acting on a received event, retrieve that exact event ID and check whether it was already acknowledged. Never treat a tap as approval for payments, permissions, credentials, or other consequential actions.

Layout writes use the authenticated same-origin `/api/layout` endpoint with layout and module-version guards; there is no MCP layout writer. Read [the setup protocol](docs/agent-setup-protocol.md) and [widget skills](agent-skills/README.md) before extending the app. Calendar and usage are snapshots, not direct server-side Google/account adapters. Scheduled ingestion requires separately authorized connected tools.

## Beta boundaries

- **Bring your deployment:** your own D1 database and a trusted `AUTHENTICATOR` service binding are required. Unconfigured data endpoints fail closed.
- **Bring authorized sources:** calendar, project and usage feeds need authorized integrations or a helper to write snapshots. The usage helper is not universally built in to every assistant environment.
- **Snapshots have limits:** observation timestamps and calendar coverage describe saved data; they do not promise live account access.
- **Delivery is asynchronous:** callback receipt and assistant acknowledgement are separate. Bounded, request-driven retries do not guarantee delivery while the panel is closed.
- **Setup still needs validation:** source tests do not establish a fresh-user install, own-data setup, public catalog availability, or marketplace approval.

## Build your own widgets

Start with the [widget authoring bundle](agent-skills/README.md): [create](agent-skills/create-dot-panel-widget/SKILL.md) or [edit](agent-skills/edit-dot-panel-widget/SKILL.md) a statically imported widget. Typed templates and snapshot model tests help preserve owner scope, freshness, and saved layouts. This is a source-editing workflow; it does not install arbitrary executable widgets at runtime.

## Development and security

See [SECURITY.md](SECURITY.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and the editable [brand kit](public/brand/README.md).

## License

Copyright (C) 2026 Dot Panel contributors.

Dot Panel application code and original brand assets are licensed under **GNU AGPL version 3 only** (`AGPL-3.0-only`). See the complete [LICENSE](LICENSE). Dependencies retain their own licenses. For modified network-hosted versions, review the AGPL's corresponding-source obligations, including section 13.

## Plugin branding

See [catalog copy, icon and connection/setup guidance](docs/plugin-branding.md). MCP metadata and tool titles are application-controlled; catalog listing fields may require a separate supported platform editor.
