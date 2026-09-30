# Optional local usage tracker

The tracker is an implemented optional local helper for **Python 3.10+ on POSIX Linux or macOS**, using Python's standard library and the existing Codex CLI. Linux checks have run; macOS remains unverified. It is separate from the private Site and from installing a skill. Its actual `--help` matches the commands below. This does not establish an independently verified cross-user installation or universally available CLI-to-panel connection.

The helper reads available usage limits for the already signed-in ChatGPT account and writes a minimal snapshot to one explicitly selected owner-private panel. It does not log in, generate credentials, purchase credits, consume resets or change account permissions. It must not inspect, replace or stop someone else's personal helper.

## Prerequisites and privacy

- Python 3.10+ and a compatible `codex` executable on this computer; no third-party Python packages required.
- Existing Codex CLI ChatGPT authentication for the intended owner. API-key-only authentication is not a substitute for this account-specific tracker. Do not ask for pasted tokens or read authentication secret files.
- The intended private panel's tools are already connected and callable through a supported local bridge, including owner identity verification and the usage snapshot writer/readback. Browser or desktop connection alone does not prove CLI availability.
- Explicit permission to read this account's usage and send the minimal snapshot to that panel. A background launch or autostart needs explicit authorization for that scope; a one-time check does not authorize a daemon.

Choose one absolute **private state directory per installation outside the repository**, restricted to the current OS user. Reuse it for every launch; another directory bypasses per-directory duplicate prevention. Configuration retains the explicit target and a hash of casefolded documented account email, not tokens. That hash is not a tenant identifier and cannot detect same-email workspace changes. The panel-name check is consistency checking, not cryptographic ownership proof; authorization depends on the connected owner-scoped server. Hashes remain private metadata and must not be published. Stop on changed identity or ambiguous target rather than silently selecting another account/panel. Explicitly reconfiguring a different account/target clears local last-good/status evidence for the previous target; it does not change the previous panel.

The official app-server reference documents `account/read` and `account/rateLimits/read`. Prefer available `rateLimitsByLimitId`; missing/null windows mean unavailable. `usedPercent` is consumption, remaining is `100 - usedPercent`, and `resetsAt` is a Unix timestamp. The installed protocol schema was generated with `codex app-server generate-json-schema --out ...` and confirms `mcpServer/tool/call` with `server`, `threadId`, `tool` and `arguments`. This proves local method shape, not universal CLI-version support or a connected destination. Verify those independently; do not guess substitute RPCs. [App-server documentation](https://learn.chatgpt.com/docs/app-server).

## Command contract

The implemented CLI is:

```text
python3 scripts/usage-tracker.py --state-dir PRIVATE configure --server S --tool-prefix P --panel-name NAME
python3 scripts/usage-tracker.py --state-dir PRIVATE once
python3 scripts/usage-tracker.py --state-dir PRIVATE run
python3 scripts/usage-tracker.py --state-dir PRIVATE start
python3 scripts/usage-tracker.py --state-dir PRIVATE status
python3 scripts/usage-tracker.py --state-dir PRIVATE stop
python3 scripts/usage-tracker.py --state-dir PRIVATE uninstall
```

`PRIVATE`, `S`, `P` and `NAME` are placeholders for verified local values, not shell commands to copy literally. Resolve the script from the retained framework checkout and quote real paths/labels normally; never place credentials in arguments.

| Command | Behavior |
| --- | --- |
| `configure` | Verify current account and selected panel identity read-only; retain private hashed identity and explicit target. No credentials or automatic process launch. |
| `once` | Perform one authorized usage read and minimal snapshot write, then verify readback. |
| `run` | Poll in the foreground until stopped. |
| `start` | Start an explicitly authorized local background process, protected by the same lock. No reboot startup. |
| `status` | Report process/liveness evidence, last attempt/success, freshness and errors without secrets; it does not print the target. A PID alone is not proof of freshness. |
| `stop` | Request this state's process to stop using its stop file; never terminate unrelated processes. Verify exit/lock release. |
| `uninstall` | Refuse while active; first stop, verify exit with status, then remove only its own private state after authorization. Preserve CLI login, panel data/layout, other helpers and unrelated files. |

Implemented lifecycle: one process per private state directory, guarded by a lock and stop file; normal polling every 60 seconds, failure backoff up to 600 seconds. Keep last-good data and its original observation time after failed reads/writes. Report staleness/unavailability honestly; never replace missing data with zero usage or fabricate a fresh timestamp. Duplicate process prevention does not establish cross-target ownership by itself.

There is **no automatic autostart**. A closed terminal can stop foreground tracking; a stopped/sleeping computer or reboot interrupts local updates. Any later systemd/launchd setup is separate, explicitly approved work and must reuse verified target/lifecycle controls. No always-on ChatGPT hosting is implied.

## Verify before calling it working

Use [manage-dot-panel-usage](../agent-skills/manage-dot-panel-usage/SKILL.md). Check helper presence, actual CLI schemas, account identity and exact connected panel first. Run one authorized sample, read back the usage snapshot, and inspect timestamp/window/reset values. Test stale-last-good behavior, identity mismatch, duplicate starts, stop and uninstall on isolated private test state. Distinguish synthetic tests from a real authenticated read/write. Linux testing is not evidence of macOS verification.

Skills can include optional executable scripts, but skill installation does not launch them or prove unattended runtime access. [Skills documentation](https://developers.openai.com/plugins/build/skills). Unsupported local bridge/account access means usage remains optional/manual; it must not block the rest of a private Dot Panel installation or cause credential/access expansion.

The script remains in the retained framework checkout; later distribution must include it and its documented source path. These local implementation checks do not prove a live authenticated cross-user write.
