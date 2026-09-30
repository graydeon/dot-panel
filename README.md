# Dot Panel

A private, touch-first status panel for an AI assistant. Questions appear only while pending. Once an answer is saved, the panel returns to project status. The assistant's name is an owner setting; Dot Panel is the product name.

## Features

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

This repository contains reusable source, not anyone's live dashboard, private links, data, credentials, or deployment history.

## Stack and commands

Node.js 22.13+ (Node 24 recommended), React, TypeScript, Vite, Cloudflare Workers, and D1.

```sh
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

## Development and security

See [SECURITY.md](SECURITY.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and the editable [brand kit](public/brand/README.md).

## License

Copyright (C) 2026 Dot Panel contributors.

Dot Panel application code and original brand assets are licensed under **GNU AGPL version 3 only** (`AGPL-3.0-only`). See the complete [LICENSE](LICENSE). Dependencies retain their own licenses. For modified network-hosted versions, review the AGPL's corresponding-source obligations, including section 13.

## Plugin branding

See [catalog copy, icon and connection/setup guidance](docs/plugin-branding.md). MCP metadata and tool titles are application-controlled; catalog listing fields may require a separate supported platform editor.
