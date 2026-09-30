// SPDX-License-Identifier: AGPL-3.0-only
import assert from 'node:assert/strict';
import {runtimeFixture} from './runtime-fixture.mjs';
const {mf}=await runtimeFixture({auth:false,local:true});
try {
 for(const headers of [{},{'oai-authenticated-user-id':'forged-user'}]) {
  const plain=await mf.dispatchFetch('https://fixture.test/api/state',{headers});assert.equal(plain.status,401);
 }
 const forged=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{'Content-Type':'application/json','oai-authenticated-user-id':'forged-user'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name:'get_touch_status',arguments:{}}})});assert.equal(forged.status,401);
 const discovery=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:2,method:'server/discover'})});assert.equal(discovery.status,200);
 const local=await mf.dispatchFetch('http://localhost/api/state');assert.equal(local.status,200);
} finally {await mf.dispose();}
const trusted=await runtimeFixture();
try {
 for(const token of ['rejected','false','empty','long','number','malformed','throws']) {
  const response=await trusted.mf.dispatchFetch('https://fixture.test/api/state',{headers:{authorization:`Bearer ${token}`,'oai-authenticated-user-id':'synthetic-owner-a'}});
  assert.equal(response.status,401,`${token} must fail closed`);
  assert.equal(response.headers.get('Cache-Control'),'no-store');
  assert.equal((await response.text()).includes('pending_questions'),false);
 }
 const started=Date.now();
 const timeout=await trusted.mf.dispatchFetch('https://fixture.test/api/state',{headers:{authorization:'Bearer timeout'}});
 assert.equal(timeout.status,401);
 assert.ok(Date.now()-started<6000,'Slow authenticator must be bounded rather than blocking for 10 seconds');
 assert.equal((await timeout.text()).includes('Synthetic provider failure'),false);
 for(const headers of [{authorization:'Bearer owner-a','oai-authenticated-user-id':'synthetic-owner-b','x-owner-id':'synthetic-owner-b'},{cookie:'fixture_session=b'}]) {
  const response=await trusted.mf.dispatchFetch('https://fixture.test/api/state',{headers});assert.equal(response.status,200);assert.deepEqual((await response.json()).pending_questions,[]);
 }
 console.log('Runtime auth passed: missing/forged identities denied, local mode confined, trusted bearer/cookie accepted, rejected/malformed/provider errors fail closed; slow provider denied within six seconds.');
} finally {await trusted.mf.dispose();}
