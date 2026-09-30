// SPDX-License-Identifier: AGPL-3.0-only
// Synthetic identities only. This is not a production authenticator or live-user proof.
import {Miniflare,convertV4MiniflareOptions} from 'miniflare';
import {build} from 'esbuild';
import {readdir, readFile} from 'node:fs/promises';
const authenticator = `export default {async fetch(request) {
 if (request.headers.has('oai-authenticated-user-id') || request.headers.has('x-owner-id')) return new Response('Forged identity forwarded', {status:500});
 if (request.headers.get('x-original-method') !== 'GET' && request.headers.get('x-original-method') !== 'POST') return new Response('Missing method', {status:500});
 if (!request.headers.get('x-original-url')?.startsWith('https://fixture.test/')) return new Response('Missing original URL', {status:500});
 const token=request.headers.get('authorization');
 if(token==='Bearer malformed') return new Response('{broken', {headers:{'Content-Type':'application/json'}});
 if(token==='Bearer rejected') return new Response('Rejected', {status:403});
 if(token==='Bearer throws') throw new Error('Synthetic provider failure');
 if(token==='Bearer timeout') await new Promise(resolve=>setTimeout(resolve,10000));
 if(token==='Bearer false') return Response.json({authenticated:false,owner_id:'synthetic-owner-a'});
 if(token==='Bearer empty') return Response.json({authenticated:true,owner_id:''});
 if(token==='Bearer long') return Response.json({authenticated:true,owner_id:'x'.repeat(257)});
 if(token==='Bearer number') return Response.json({authenticated:true,owner_id:123});
 const owner=token==='Bearer owner-a'?'synthetic-owner-a':token==='Bearer owner-b'?'synthetic-owner-b':request.headers.get('cookie')==='fixture_session=b'?'synthetic-owner-b':null;
 return Response.json({authenticated:!!owner,owner_id:owner});
}};`;
export async function runtimeFixture({auth=true, local=false,sites=false}={}) {
 const bundled=await build({entryPoints:[sites?'worker/sites.ts':'worker/index.ts'],bundle:true,platform:'neutral',format:'esm',external:['cloudflare:workers'],write:false});
 const mf=new Miniflare(convertV4MiniflareOptions({workers:[{name:'panel',modules:true,script:bundled.outputFiles[0].text,compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB'],bindings:local?{LOCAL_DEV_MODE:'true',LOCAL_DEV_USER:'fixture-local'}:{},...(!sites&&auth?{serviceBindings:{AUTHENTICATOR:'auth'}}:{})}, {name:'auth',modules:true,script:authenticator,compatibilityDate:'2026-05-15'}]}));
 const db=await mf.getD1Database('DB','panel');
 for(const file of (await readdir('drizzle')).filter(name=>name.endsWith('.sql')).sort()) {
  const sql=await readFile(`drizzle/${file}`,'utf8');
  await db.exec(sql.replaceAll('--> statement-breakpoint','').replaceAll('\n',' '));
 }
 return {mf,db};
}
export async function callTool(mf,token,name,args={}) {
 const response=await mf.dispatchFetch('https://fixture.test/mcp',{method:'POST',headers:{'Content-Type':'application/json',authorization:`Bearer ${token}`,'oai-authenticated-user-id':'synthetic-owner-b'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name,arguments:args}})});
 return {response,body:await response.json()};
}
