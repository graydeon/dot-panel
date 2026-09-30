// SPDX-License-Identifier: AGPL-3.0-only
import type {PanelModule} from '@/lib/panel-config';

// A normal module config entry. No runtime loader reads this file.
// Rename once before first use; keep id and snapshot_key stable afterward.
export const workflowModule = {
  id: 'workflow-snapshot',
  title: 'Workflow snapshot',
  kind: 'project',
  placement: 'secondary',
  enabled: true,
  source_type: 'manual',
  mode: 'agent_snapshot',
  snapshot_key: 'Workflow snapshot',
  links: [],
} satisfies PanelModule;
