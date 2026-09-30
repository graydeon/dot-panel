# Dot Panel release candidate

**Package:** `dot-panel` · **Version:** `1.0.0-rc.1` · **License:** AGPL-3.0-only

This is the installable skills framework, not a hosted account or a raw source archive. It includes five skills: setup, maintenance, create/edit widgets and optional local usage tracking. The retained source is at `assets/framework/`; original branding and license/notices are included. A private panel uses the Site-provisioned plugin created during the owner's own setup, not a shared MCP endpoint in this installer.

## Start with a draft or supported local install

For the publishing portal, choose the intended organization/project and your verified developer identity, then upload this ZIP as a **draft**. Package validation is separate from approval. Stop before review submission/publication until the remaining validation and identity/privacy checks are resolved. `graydeon` is the verified public GitHub handle in this candidate; it is not a claim about the portal's verified legal identity. If your selected publisher differs, reconcile metadata before submission. Skills-only directory eligibility and automated scans remain platform decisions.

On a supported local client, a separate local/repo marketplace can load the extracted plugin root. Do not overwrite an existing personal plugin or marketplace. Local install success does not prove ChatGPT portal acceptance or public directory installation.

After installation, ask: **“Set up my private Dot Panel with the modules I choose.”** The setup skill checks available Sites capabilities, retains/copies the sanitized template into your own private installation, privately deploys it using the Sites adapter, connects the provisioned plugin and verifies a harmless question/answer workflow. User clicks or platform approvals may be required. Without Sites tools, report the prerequisite; this ZIP does not unlock unavailable platform capabilities. Preserve existing private installations and layouts.

Optional local usage tracking needs Python 3.10+ on POSIX, existing ChatGPT-authenticated Codex CLI and the intended private panel's callable local tools. Linux is tested; macOS and independent-user bridge setup are unverified, Windows is unsupported. Installing a skill does not launch a helper. Authorize any background start explicitly. No reboot autostart, new credentials or central service is included.

## Validate this exact candidate

See `PROVENANCE.json` for the pinned source commit, `PACKAGE_CONTENTS.json` for file hashes and `assets/framework/SOURCE_MANIFEST.json` for retained-source integrity. Package tooling checks the manifest schema, listing lengths, safe ZIP paths, skill links and original assets. Rebuild/test the retained source in a separate directory with Node 24 and Python 3.10+:

```sh
npm ci
npm audit --audit-level=moderate
npm test
npm run test:template
npm run test:recovery
npm run test:usage
npm run test:runtime
npm run build
npm run build:sites
python3 scripts/check-docs.py
```

These commands run from the copied `assets/framework` directory. Local runtime tests bind synthetic loopback services; they do not provision a Site or read personal accounts. The helper's help is `python3 scripts/usage-tracker.py --help`.

## What is not established

A current-owner synthetic private install and actual tap-to-webhook-to-acknowledgement workflow passed against the earlier pinned Sites source. That is not independent-user proof. The exact ZIP still needs platform draft checks, fresh-user setup and real iPad/VoiceOver checks. Hosted identity-header probes were blocked by the edge rather than independently verified; synthetic owner-isolation tests pass. Live helper read/write for a new installation and hosted recovery/longer pilot validation remain separate evidence. No v1 tag, final release, catalog approval or public publication is implied.
