// SPDX-License-Identifier: AGPL-3.0-only
import assert from 'node:assert/strict';
import {workflowModule} from './manifest';
import {snapshotView} from './snapshot-model';
const time = Date.parse('2026-01-01T12:00:00Z');
const row = {name:workflowModule.snapshot_key,update:'Synthetic example only',source_timestamp:'2026-01-01T11:59:00Z'};
assert.equal(snapshotView(workflowModule,[],time,120_000).status,'missing');
assert.equal(snapshotView(workflowModule,[row],time,120_000).status,'fresh');
assert.equal(snapshotView(workflowModule,[row],time,1_000).status,'stale');
assert.equal(snapshotView(workflowModule,[{...row,name:'Unrelated'}],time,120_000).status,'missing');
assert.equal(snapshotView(workflowModule,[{...row,source_timestamp:'invalid'}],time,120_000).status,'invalid');
assert.equal(snapshotView(workflowModule,[{...row,source_timestamp:'2026-01-02T12:00:00Z'}],time,120_000).status,'invalid');
assert.equal(snapshotView({...workflowModule,mode:'link_only'},[row],time,120_000).status,'link-only');
assert.equal(snapshotView({...workflowModule,title:'Renamed title'},[row],time,120_000).text,row.update);
console.log('Snapshot starter: 8 assertions passed');
