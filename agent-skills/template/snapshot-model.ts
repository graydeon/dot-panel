// SPDX-License-Identifier: AGPL-3.0-only
import type {PanelModule} from '@/lib/panel-config';

// Matches overview.projects in lib/status-updates.ts; not a new server schema.
export type ProjectSnapshot = {
  name: string;
  update: string;
  source_timestamp: string;
  source_url?: string;
};
export type SnapshotView = {
  status: 'missing' | 'invalid' | 'fresh' | 'stale' | 'link-only';
  text: string;
  sourceTime: string | null;
};

// Supply the workflow's freshness budget explicitly; no background fetching.
export function snapshotView(
  module: PanelModule,
  projects: readonly ProjectSnapshot[],
  nowMs: number,
  staleAfterMs: number,
): SnapshotView {
  if (module.mode === 'link_only') return {status:'link-only',text:'Reference links',sourceTime:null};
  const match = projects.find(p => p.name === (module.snapshot_key ?? module.title));
  if (!match) return {status:'missing',text:'No verified update yet',sourceTime:null};
  const stamp = Date.parse(match.source_timestamp);
  if (!Number.isFinite(stamp) || !Number.isFinite(nowMs) || !Number.isFinite(staleAfterMs) || staleAfterMs < 0 || stamp > nowMs + 300_000) {
    return {status:'invalid',text:'Snapshot time unavailable',sourceTime:null};
  }
  return {status:nowMs - stamp > staleAfterMs ? 'stale' : 'fresh',text:match.update,sourceTime:new Date(stamp).toISOString()};
}
