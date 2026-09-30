# Dot Panel data handling

Dot Panel is an AGPL-licensed framework and agent skill collection maintained in the public `graydeon/dot-panel` repository. The maintainer does not operate a central dashboard service or receive your panel contents through this framework. This notice describes the bundled software; it does not replace ChatGPT, Sites, Codex or connected providers' privacy policies.

## Your private installation

Your dot creates your own private Site through available platform tools. With your authorization, it can save your assistant display name, module references and links, portrait/landscape layouts, ordinary questions and answers, project/calendar/usage snapshots and their timestamps. Your Site's database stores this information under authenticated owner scope. Answer delivery stores subscription configuration, callback secrets and retry/acknowledgement records server-side. Callback destinations receive the ordinary answer event you authorize. Do not put credentials, sensitive records or consequential approvals into questions, links or snapshots.

The software retains saved records until the owner removes/replaces them or deletes the installation; it does not include an automatic age-based purge. Private backups, provider retention, platform request logs and infrastructure metadata depend on the platform and storage you use. The maintainer cannot independently erase platform copies or promise their retention periods. Runtime diagnostics can include delivery/verification status and error categories; do not publish private logs, deployment configuration, databases or backups.

## Optional integrations and local usage helper

Source integrations remain under your existing account permissions. The assistant should read only requested sources and store the minimum useful snapshot. A source link is not an access grant. The optional local helper reads limits/reset metadata from an already signed-in Codex account and sends only normalized usage values and timestamps to your explicitly selected private panel. It keeps private local target configuration, a hash of the documented account email, status and last-good snapshots. It does not export tokens, sign in, consume resets or start automatically on installation. Only use it with an authorized local account and panel connection.

## Controls and support

Review modules and feeds before enabling them. Dismiss cancels an ordinary pending question without producing an answer event; it is not a history-erasure operation. Stop/uninstall the optional helper to stop local refreshes; uninstall removes its own local configuration/status/last-good files while preserving Codex sign-in and the remote snapshot. Manage private Site data, access, subscriptions, backups and deletion through the supported platform workflow. Required platform confirmations remain in force.

The package contains reusable source, original artwork and synthetic tests, not another owner's configuration or data. No telemetry or external analytics collector is bundled. Public GitHub issues are visible to others: report problems using synthetic examples and redact account details, private URLs, tokens, database contents and histories. Support is through [GitHub issues](https://github.com/graydeon/dot-panel/issues); no response-time guarantee is offered.
