// SPDX-License-Identifier: AGPL-3.0-only
import type {Widget} from '@/lib/layout-model';
import {snapshotView, type ProjectSnapshot} from './snapshot-model';

// Statically import in the panel and invoke from renderWidget for this module ID.
// Keep modal ownership in the existing panel; this component never fetches or saves.
export default function SnapshotWidget({widget,projects,nowMs,staleAfterMs,onOpen}: {
  widget: Widget;
  projects: readonly ProjectSnapshot[];
  nowMs: number;
  staleAfterMs: number;
  onOpen: (trigger: HTMLButtonElement) => void;
}) {
  if (!widget.module) return null;
  const view = snapshotView(widget.module,projects,nowMs,staleAfterMs);
  return <article className={`module-widget tile module-${widget.module.placement}`}>
    <button className="module-details" onClick={event => onOpen(event.currentTarget)}>
      <h2>{widget.title}</h2>
      <p>{view.text}</p>
      <small>{view.status === 'stale' ? 'Stale snapshot · ' : ''}{view.sourceTime
        ? <time dateTime={view.sourceTime}>Source: {view.sourceTime}</time>
        : view.status === 'link-only' ? 'Link only' : 'Not synced'}</small>
    </button>
  </article>;
}
