// SPDX-License-Identifier: AGPL-3.0-only
export interface AuthEnv {AUTHENTICATOR?:Fetcher;LOCAL_DEV_MODE?:string;LOCAL_DEV_USER?:string;}
/** A trusted deployment-owned service must verify the session/token and return a stable owner ID. */
export async function principal(request:Request,env:AuthEnv):Promise<string|null>{
 const hostname=new URL(request.url).hostname;
 if(env.LOCAL_DEV_MODE==='true'&&['localhost','127.0.0.1','[::1]'].includes(hostname)&&env.LOCAL_DEV_USER)return env.LOCAL_DEV_USER;
 if(!env.AUTHENTICATOR)return null;
 const headers=new Headers();for(const name of ['authorization','cookie']){const value=request.headers.get(name);if(value)headers.set(name,value);}
 headers.set('x-original-url',request.url);headers.set('x-original-method',request.method);
 const controller=new AbortController();
 let timeout:ReturnType<typeof setTimeout>|undefined;
 try{
  const rejected=new Promise<null>(resolve=>{timeout=setTimeout(()=>{controller.abort();resolve(null);},3000);});
  const verified=(async()=>{
   const response=await env.AUTHENTICATOR!.fetch(new Request('https://auth.internal/verify',{headers,signal:controller.signal}));
   if(!response.ok)return null;
   const result=await response.json() as {authenticated?:boolean,owner_id?:unknown};
   return result.authenticated===true&&typeof result.owner_id==='string'&&result.owner_id.length>0&&result.owner_id.length<=256?result.owner_id:null;
  })();
  return await Promise.race([verified,rejected]);
 }catch{return null;}finally{if(timeout!==undefined)clearTimeout(timeout);}
}
