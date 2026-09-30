// SPDX-License-Identifier: AGPL-3.0-only
// Test only the application behind a trusted synthetic Sites hosting boundary.
// These directly injected headers do NOT prove live hosting strips forged client headers.
import assert from 'node:assert/strict';
import {runtimeFixture} from './runtime-fixture.mjs';
const {mf,db}=await runtimeFixture({sites:true});
const identities=['fixture-platform-opaque-a','fixture-platform-opaque-b'];
const email='fixture-unused@example.invalid';
const headers=(owner)=>({...owner?{'oai-authenticated-user-id':owner}:{},'oai-authenticated-user-email':email});
const rpc=async(owner,method,params={})=>{
 const response=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{...headers(owner),'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});
 return {status:response.status,text:await response.text()};
};
try {
 for(const owner of [undefined,'','x'.repeat(257)]) {
  for(const path of ['state','layout','calendar','usage']) {
   const response=await mf.dispatchFetch(`https://fixture.test/api/${path}`,{headers:headers(owner)});
   assert.equal(response.status,401,`${path} rejects absent/invalid ID`);assert.equal(response.headers.get('Cache-Control'),'no-store');
  }
  const call=await rpc(owner,'tools/call',{name:'get_touch_status',arguments:{}});assert.equal(call.status,401);assert.equal(call.text.includes('pending_questions'),false);
 }
 const discovery=await rpc(undefined,'server/discover');assert.equal(discovery.status,200);assert.equal(discovery.text.includes('pending_questions'),false);
 for(const [index,owner] of identities.entries()) {
  const set=await rpc(owner,'tools/call',{name:'set_dot_display_name',arguments:{dot_display_name:`Synthetic owner ${index}`}});assert.equal(set.status,200);assert.equal(JSON.parse(set.text).result.isError,false);
  const queue=await rpc(owner,'tools/call',{name:'enqueue_touch_question',arguments:{request_id:'same-fixture-platform-question',question:`Synthetic preference ${index}`,choices:['Yes','No']}});assert.equal(JSON.parse(queue.text).result.isError,false);
 }
 for(const [index,owner] of identities.entries()) {
  const response=await mf.dispatchFetch('https://fixture.test/api/state',{headers:headers(owner)});assert.equal(response.status,200);
  const state=await response.json();assert.equal(state.dot_display_name,`Synthetic owner ${index}`);assert.equal(state.pending_questions.length,1);assert.equal(state.pending_questions[0].text,`Synthetic preference ${index}`);
 }
 const stored=(await db.prepare('SELECT owner,dot_display_name FROM owner_settings ORDER BY owner').all()).results;
 assert.deepEqual(stored.map(row=>row.owner),identities);assert.equal(JSON.stringify(stored).includes(email),false,'Secondary raw email header must not become owner identity');
 const cross=await mf.dispatchFetch('https://fixture.test/api/settings',{method:'POST',headers:{...headers(identities[0]),origin:'https://attacker.invalid','Content-Type':'application/json'},body:JSON.stringify({dot_display_name:'Changed'})});assert.equal(cross.status,409);
 assert.equal((await db.prepare('SELECT dot_display_name FROM owner_settings WHERE owner=?').bind(identities[0]).first()).dot_display_name,'Synthetic owner 0');
 console.log('Sites application boundary passed: anonymous discovery without data, empty/oversized IDs denied, opaque synthetic owner isolation, secondary email ignored, cross-origin writes denied. Live hosting identity verification/forged-header stripping remains unverified.');
} finally {await mf.dispose();}
