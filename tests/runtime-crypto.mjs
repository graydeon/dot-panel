import {Miniflare} from 'miniflare';
import {build} from 'esbuild';
import assert from 'node:assert/strict';
const bundled=await build({entryPoints:['tests/runtime-crypto.ts'],bundle:true,platform:'neutral',format:'esm',external:['cloudflare:workers'],write:false});
const mf=new Miniflare({modules:true,script:bundled.outputFiles[0].text,compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat']});
try{const r=await mf.dispatchFetch('https://fixture.test');const value=await r.json();console.log('Cloudflare runtime crypto/signature/Request:',r.status,value);assert.equal(r.status,200);assert.equal(value.ok,true);}finally{await mf.dispose();}
