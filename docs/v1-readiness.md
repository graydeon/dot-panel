# Framework v1 readiness ledger

Updated 30 September 2026. This is implementation evidence, not v1 approval. The beta tag remains unchanged. No submission ZIP, private deployment or public catalog release was created by these checks.

## Product and installation route

Dot Panel is a free AGPL-3.0-only framework, templates and traditional agent skills. Each user's dot creates that user's own private panel in Sites, optionally linked in Spaces, and connects the provisioned private Site plugin. There is no central dashboard service, shared OAuth provider or developer account credential bundled for users.

[Installation](framework-installation.md), [setup skill](../agent-skills/setup-dot-panel/SKILL.md) and [maintenance skill](../agent-skills/maintain-dot-panel/SKILL.md) define explicit available-tool prerequisites and create-once/resume behavior. Sites manages authentication for its private plugin. The installer is intended to be skills-only; official [package](https://developers.openai.com/plugins/build/plugins) and [submission](https://developers.openai.com/plugins/deploy/submission) documentation permit skills, MCP or both. Package acceptance and actual public installation are unverified. No canonical public Sites dependency was resolved; no App ID is invented.

## Evidence against release gates

| Gate | Verified implementation/checks | Still required |
| --- | --- | --- |
| Installation | Sites-only entrypoint; retained build emits client/server output; setup/maintenance skills validate; read-only setup evidence tool | Fresh independent install/connection and resume; live forged-header/revocation boundary checks |
| Preferences | Two to six distinct choices; old three-choice compatibility; dismissal creates no answer; consequential approvals explicitly separate; accurate replacement/cancellation annotations | Twenty routing/approval cases through actual dot, ordinary prompt routing and real modal taps |
| Reliability | Atomic answer/outbox, exact-event lookup, bounded retries and signed request tests; 100 distinct synthetic question transactions across duplicates/conflicts/answer-versus-dismiss plus snapshot revision guards | Real client subscribe→tap→event→ack, renewal/expiry and outage recovery traces; measured latency |
| Feeds | Timestamped calendar/project/usage snapshots; pure missing/invalid/stale/fresh boundaries; visible usage snapshot age | Independent optional feed exercise, failed-read freshness and owner-controlled scheduling proof |
| Layout/accessibility | Geometry and palette checks; scrollable six-choice modal/editor; explicit focus indicators; Radix name dialog focus handling | Broader browser/device render regression and actual iPad portrait/landscape, Safari and VoiceOver validation |
| Recovery/extensions | Seven SQL migrations rehearsed with two synthetic owners; records/uniqueness preserved; failed transaction rollback and whole-db restore; eight widget starter assertions; runbook | Actual private Site upgrade/restore/rollback, independently authored widget and preservation proof |
| Distribution/support | AGPL/license/notice integrity, meaningful app CI added, full dependency audit reports zero advisories | Candidate CI success, publisher/skill scans, listing/review/approved publication; support and operator retention decisions |

Local domain suite: **38 counted tests**, including dismissal (previous beta printed its summary before that regression). Runtime suites use real Miniflare/SQLite-backed D1 with synthetic owners, not live accounts. Both generic public Worker and Sites-only routes are tested. Generic malformed/stalled auth fails closed; Sites tests assume the hosting boundary injects the trusted opaque owner ID. They do not prove a live Site strips forged headers.

Widget model: eight starter assertions. Recovery: seven migrations and two synthetic owners. Standard and Sites builds typecheck and bundle successfully. Full production and development npm audit on this date reports zero known advisories after patched Vite/esbuild/Drizzle/Wrangler tooling. Wrangler pins its matching Miniflare 5 alpha dependency; runtime fixtures use the provided v4-options converter and retain their existing assertions. Clean lockfile installation and isolated migration generation are checked. This is not a complete security assessment. Full device/browser checks could not run: the available CLI requires a Chromium version not installed in this executor. No human testers, device sessions or review results are simulated.

## Honesty and remaining work

The personal usage helper remains a private standalone process, not a universal built-in feed. Snapshots do not establish live connector access. Request-driven delivery does not promise closed-page autonomous retries. Skills cannot invoke unavailable APIs or bypass account policy/required confirmations. Installing the framework does not automatically connect a private Site or authorize a subscription.

The proposed roadmap's independent setup, routing, device, recovery, extension and seven-day/three-owner pilot gates remain open until evidence is recorded. Do not shorten those gates to meet a clock deadline. Complete and verify the corrected code/setup flow before packaging a tested candidate; public release still follows evidence review and external directory approval.

## Current-owner private Sites test checkpoint

The separate Site-owning task reports successful private retained-source deployment and plugin installation/read calls against `bd3dd24`, authenticated naming/empty UI, and actual Dismiss interaction with no answer/outbox record while preserving another designated question. After task dedup and correcting filtered-subscription ordering, its connection reports active. This is one current-owner test instance with synthetic content; the original personal panel remains protected. Callback/acknowledgement is still being checked at this checkpoint. No private IDs or URLs are included here.

These results do not prove independent first-user setup, another real identity, forged-header overwrite/revocation, iPad/VoiceOver, hosted recovery or public installer distribution. The development-tool follow-up does not deploy or change either private Site.
