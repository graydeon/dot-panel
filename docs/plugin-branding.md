# Dot Panel plugin listing and setup

## Proposed catalog copy

**Name:** Dot Panel

**Short description:** Touch dashboard for your dot

**Full description:** A free AGPL framework and agent skill collection for your own dot to create and maintain your private panel in ChatGPT Sites. Keep your assistant’s work in view. Dot Panel brings timestamped project updates, a Needs You decision queue, calendar snapshots and scoped usage limits into a personal touch-first dashboard. Answer ordinary yes/no and multiple-choice questions, choose the modules that matter, and save separate portrait and landscape layouts. Light and dark themes keep it comfortable on a tablet or desktop. Your assistant prepares updates from sources you have authorized; the panel clearly shows snapshot freshness and calendar coverage.

**Icon:** `public/brand/favicon-180.png` (180 × 180 PNG). The editable original is `public/brand/favicon.svg`. The red dot in a near-black panel matches the existing original brand kit. No account-specific text or data is embedded.

## Suggested starting prompts

- Set up my Dot Panel with the projects and modules I choose
- Refresh my panel from the sources I have connected
- Add an ordinary yes/no decision to Needs You
- Show me when my calendar and usage were last checked

These are proposed listing copy, not a platform-installed prompt menu.

## Setup checklist

1. Use the framework setup skill and supported Sites tools to create your own private panel, then connect its Site-provisioned plugin through the platform’s supported connection flow.
2. Verify a read-only status call. Read current config before changing anything.
3. Set the owner’s actual assistant name. Review modules, source references, links and timezone with the owner. Preserve existing initialized configuration.
4. Read source apps using already-authorized tools, then store minimal snapshots with real timestamps and coverage. Calendar is read-only; no invitation or editing tools are provided.
5. Configure answer-event delivery only with the owner’s requested destination and platform subscription flow. Verify a harmless decision end to end; never treat a choice as consequential authorization.
6. Let the owner use Edit layout to save their preferred portrait and landscape arrangements. Source updates must not reset these layouts.
7. Set up recurring refresh only when requested and the source/write access has been verified.

See [the full setup protocol](agent-setup-protocol.md) and [the source repository](https://github.com/graydeon/dot-panel).

## Privacy and operational boundaries

The existing hosted panel remains owner-private. User data is scoped to the authenticated owner; callback secrets stay server-side. Calendar and usage displays are snapshots rather than direct live account connections. Delivery retries are bounded and request-driven, and an accepted webhook is separate from an assistant acknowledgement. The public repository contains reusable source only.

This document is product/setup information, not a privacy policy, legal agreement, marketplace approval or security certification. Public distribution of the skills framework requires its own platform review and truthful prerequisite/privacy descriptions. Each private panel uses Sites-managed identity. No central hosted service or external auth provider is a prerequisite.

## Metadata actually under application control

MCP initialize/discovery advertises the Dot Panel title, description, version and original PNG icon. Tool discovery provides readable titles while retaining stable tool IDs and schemas. Website metadata includes the product description, favicon and Apple touch icon. Client support for displaying MCP icons/titles varies.

The current Sites metadata tool edits only the Site title. No catalog icon, catalog description, suggested-prompts or marketplace-publication write operation is exposed in the installed tool surface. Updating MCP metadata does not prove that the catalog description changed. Tool refresh can pick up server metadata, but cannot be assumed to edit a separately stored catalog listing. Reuse the existing plugin identity; do not create a replacement to change branding.
