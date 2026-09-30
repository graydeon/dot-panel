// SPDX-License-Identifier: AGPL-3.0-only
import {Miniflare} from 'miniflare';
import {build} from 'esbuild';
import assert from 'node:assert/strict';
const bundled=await build({entryPoints:['worker/index.ts'],bundle:true,platform:'neutral',format:'esm',external:['cloudflare:workers'],write:false});
const mf=new Miniflare({modules:true,script:bundled.outputFiles[0].text,compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB']});
try{
 const plain=await mf.dispatchFetch('https://fixture.test/api/state');assert.equal(plain.status,401);
 const forged=await mf.dispatchFetch('https://fixture.test/api/state',{headers:{'oai-authenticated-user-id':'forged-user'}});assert.equal(forged.status,401);
 const mcp=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{'Content-Type':'application/json','oai-authenticated-user-id':'forged-user'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name:'get_touch_status',arguments:{}}})});assert.equal(mcp.status,401);
 const discovery=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:2,method:'server/discover'})});assert.equal(discovery.status,200);
 console.log('Production auth boundary passed: anonymous/forged identities denied; non-private discovery works');
}finally{await mf.dispose();}
