---
name: manage-dot-panel-usage
description: Configure, verify, run, inspect or remove the optional Python local Dot Panel usage tracker for the requesting user's existing ChatGPT-authenticated Codex CLI and explicitly connected private panel. Use only for requested local tracking; does not install credentials, imply universal support, or automatically enable background startup.
---

# Manage optional local usage tracking

Follow [the usage tracker guide](../../docs/usage-tracker.md). This is a Python 3.10+ POSIX Linux/macOS local helper (Linux tested; macOS unverified), not a universal built-in feed or always-on ChatGPT process. Installing the skill or connecting once does not start tracking. Do not modify the original owner's personal process or any unrelated helper.

## Check capability and scope

1. Confirm the user requested this operation and identify their intended private panel. One-time sampling, foreground polling, background launch, stopping/removing this installation and future autostart are different scopes. Obtain explicit permission for background/autostart if not already authorized; ordinary panel answers cannot bypass required platform approvals.
2. Check Python 3.10+, existing Codex CLI, retained `scripts/usage-tracker.py` and its current help. The script and CLI help are implemented, but a compatible installed CLI and connected destination remain user-specific prerequisites. If absent/incompatible, report the exact prerequisite; do not fabricate success or invoke guessed commands.
3. Verify existing account identity through supported read-only CLI/app-server operations and the exact panel's connected tools. The CLI must already authenticate the intended ChatGPT account. Do not generate tokens, inspect secret files, log in/logout, add grants or assume another client's connection works here. If the supported panel invocation/identity bridge is missing, stop this optional feature and report it.
4. Select an absolute private state directory outside public source with owner-only access. Read only this tracker's state. Reuse one state directory for every launch of this installation; other directories bypass its duplicate guard. Configuration retains explicit target and hashed casefolded account email, no tokens. The hash cannot detect same-email workspace changes. Panel-name consistency is not cryptographic ownership proof; hashes are not authentication. Do not print/publish private configuration or account metadata.

## Use the actual verified CLI

Implemented command shape is `python3 scripts/usage-tracker.py --state-dir PRIVATE COMMAND`; verify actual help before use. `configure` takes `--server S --tool-prefix P --panel-name NAME`, all resolved from the user's verified connected panel. Never guess a personal endpoint or use another owner's values.

- `configure`: read-only account/panel checks, then private target/hashed-identity retention; no automatic launch.
- `once`: an authorized minimal usage sample/write with readback.
- `run`: foreground 60-second polling.
- `start`: explicitly authorized background polling; not reboot startup.
- `status`: process evidence plus observation age/last success/error, without secrets or target output.
- `stop`: request this tracker's stop file and verify it exited; do not kill by broad process matching.
- `uninstall`: refuses active tracking; first stop and verify exit, then remove only this tracker's state when authorized; retain CLI login, panel snapshots/layout and other helpers.

Use a lock/stop-file lifecycle to prevent duplicates for the selected state directory. Failures back off up to 600 seconds and preserve last-good data with its original timestamp. Identity mismatch stops writes. Missing windows mean unavailable; do not publish zero/unlimited or claim an unsuccessful refresh was fresh. Never purchase credits, consume resets or send account messages as part of tracking.

## Verify and hand off

Run one permitted real sample and read back the exact panel snapshot. Verify window/bucket/reset semantics against the current schema. Report stale/unavailable values separately. Check isolated lifecycle tests where appropriate; simulations do not prove authenticated CLI-to-panel support. Do not repeat personal-data reads or launches merely to populate evidence.

State whether tracking is configured, actually running foreground/background, or stopped; give last observed time and remaining capability gaps. Autostart is absent by default. Sleep/reboot/offline states interrupt local updates. A future systemd/launchd installation requires separate explicit authorization and testing; no portable cross-platform success is inferred from Linux tests.

Official documentation permits optional scripts in skills and describes app-server account/rate-limit reads. It does not make this particular panel bridge or always-on ChatGPT execution universally available: [skills](https://developers.openai.com/plugins/build/skills), [app-server](https://learn.chatgpt.com/docs/app-server).

Local generated Codex protocol confirms `mcpServer/tool/call` fields `server`, `threadId`, `tool` and `arguments`; do not infer every installed version or destination supports it. Retain the framework script path; later packaging must include its source.
