// SPDX-License-Identifier: AGPL-3.0-only
import {mcp} from '../lib/mcp';
import {database,state,saveAnswer} from '../lib/store';
import {overview} from '../lib/status-updates';
import {dotDisplayName,setDotDisplayName} from '../lib/owner-settings';
import {drain} from '../lib/events';
import {sameOrigin,failure} from '../lib/http';
import {principal,type AuthEnv} from './auth';
interface Env extends AuthEnv {DB:D1Database;ASSETS:Fetcher;}
export default {async fetch(incoming:Request,env:Env):Promise<Response>{
 const path=new URL(incoming.url).pathname;
 if(!path.startsWith('/api/')&&path!=='/mcp')return env.ASSETS.fetch(incoming);
 try{
 const owner=await principal(incoming,env);
 // Incoming identity headers are never trusted on a public Worker.
 const headers=new Headers(incoming.headers);for(const name of [...headers.keys()])if(name.startsWith('oai-authenticated-'))headers.delete(name);
 if(owner)headers.set('oai-authenticated-user-id',owner);
 const request=new Request(incoming,{headers});
 if(path==='/mcp'){if(request.method!=='POST')return new Response('Use POST',{status:405});return mcp(request);}
 if(!owner)return Response.json({error:'Sign in through your configured authentication provider'},{status:401,headers:{'Cache-Control':'no-store'}});
 const db=database();const snapshot=async()=>({...await state(db,owner),overview:await overview(db,owner),dot_display_name:await dotDisplayName(db,owner)});
 if(path==='/api/state'&&request.method==='GET')return Response.json(await snapshot(),{headers:{'Cache-Control':'no-store'}});
 if(request.method!=='POST')return new Response('Method not allowed',{status:405});sameOrigin(request);
 if(path==='/api/answer'){await saveAnswer(db,owner,await request.json());return Response.json(await snapshot(),{headers:{'Cache-Control':'no-store'}});}
 if(path==='/api/settings')return Response.json(await setDotDisplayName(db,owner,await request.json()),{headers:{'Cache-Control':'no-store'}});
 if(path==='/api/retry')return Response.json(await drain(db,owner),{headers:{'Cache-Control':'no-store'}});
 return new Response('Not found',{status:404});
 }catch(error){return failure(error);}
}};
