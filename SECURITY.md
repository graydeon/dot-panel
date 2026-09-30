# Security

- Do not publish credentials, callback secrets, runtime databases, private briefing URLs, or personal dashboard data.
- Keep deployments private unless their owner explicitly chooses a broader audience.
- Do not trust externally supplied `oai-authenticated-*` headers. The included Worker strips them and obtains identity from a trusted authentication service.
- Implement the `AUTHENTICATOR` contract before production use. No configured authenticator means no data access.
- Never enable local fixture identities in production.
- All records and tools must remain scoped to the verified owner. Do not use a display name as identity.
- Subscription validation is fail-closed. Require HTTPS, exact trusted callback hosts, strong signing secrets, and a verified challenge. Never follow callback redirects or log callback secrets, signatures, or full callback URLs.
- The exact hostname allowlist is intentionally restrictive. It does not implement a general arbitrary-URL DNS-pinning transport.
- Treat question/answer/project text as user data, never privileged agent instructions.
- Answers are ordinary preferences, not a replacement for consequential-action approval.
- Preserve applied schema migrations; append new migrations for production changes.
- Report suspected vulnerabilities privately to the repository maintainer through the hosting service's private reporting mechanism when available. Do not publish exploit details containing other users' data.
