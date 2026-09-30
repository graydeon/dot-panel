// SPDX-License-Identifier: AGPL-3.0-only
import {dotDisplayName} from './owner-settings';
import {readPanelConfig} from './panel-config';
import {overview} from './status-updates';
import {readCalendar} from './calendar-store';
import {readUsage} from './usage-store';
export const setupStatusTool={name:'get_panel_setup_status',description:'Read owner-scoped guided setup evidence and next steps. Does not connect sources, change settings, certify public installation, or authorize actions. Missing snapshots are not connection failures or unlimited usage.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}};
export {freshness} from './freshness';
import {freshness} from './freshness';
export async function setupStatus(db:D1Database,owner:string){
 const [name,config,status,calendar,usage]=await Promise.all([dotDisplayName(db,owner),readPanelConfig(db,owner),overview(db,owner),readCalendar(db,owner),readUsage(db,owner)]);
 const modules=config.modules.filter(m=>m.enabled).map(m=>{
  const project=status?.projects.find(p=>p.name===(m.snapshot_key??m.title));
  const observed=m.mode==='link_only'?null:m.kind==='calendar'?calendar?.source_synced_at??null:project?.source_timestamp??null;
  return {id:m.id,title:m.title,mode:m.mode,source_type:m.source_type,observation_status:m.mode==='link_only'?'link_only':freshness(observed),observed_at:observed};
 });
 const checks={assistant_name:!!name,owner_reviewed_modules:config.initialized,source_observations:modules.every(m=>m.observation_status==='fresh'||m.observation_status==='link_only')};
 const next_steps:string[]=[];
 if(!checks.assistant_name)next_steps.push('Confirm the assistant display name with the owner before saving it.');
 if(!checks.owner_reviewed_modules)next_steps.push('Review selected modules, sources, links, timezone and visibility with the owner; preserve any saved configuration.');
 if(!checks.source_observations)next_steps.push('Supply a minimal timestamped observation as explicit tool input, or review unavailable/manual/link-only mode with the owner. This plugin does not fetch external sources.');
 next_steps.push('Verify a harmless answer through the real connected client, retrieve its exact event and acknowledge only after handling it. This read cannot certify that external test.');
 return {configuration_version:config.version,checks,modules,usage:{observation_status:freshness(usage?.fetched_at??null),observed_at:usage?.fetched_at??null,provider:'authorized snapshot writer required; no universal built-in usage integration'},completion:'requires_external_verification',next_steps,limits:{freshness_threshold_minutes:60,public_installation:'not_certified_by_this_tool',consequential_approval:'required platform approval remains separate'}};
}
