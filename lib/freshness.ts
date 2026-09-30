// SPDX-License-Identifier: AGPL-3.0-only
export function freshness(timestamp:string|null,checkedAt=Date.now(),maxAgeMs=3600000){if(!timestamp)return 'missing';const time=Date.parse(timestamp);if(!Number.isFinite(time)||time>checkedAt+300000)return 'invalid';return checkedAt-time>maxAgeMs?'stale':'fresh';}
