// SPDX-License-Identifier: AGPL-3.0-only
export type FlightState={busy:boolean,queued:boolean};
/** Ordinary timer ticks coalesce; an urgent saved answer gets one immediate follow-on. */
export async function withUrgentFollowUp(state:FlightState,operation:()=>Promise<void>,urgent=false):Promise<void>{if(state.busy){if(urgent)state.queued=true;return;}state.busy=true;try{await operation();}finally{state.busy=false;if(state.queued){state.queued=false;await withUrgentFollowUp(state,operation);}}}
