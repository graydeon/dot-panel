// SPDX-License-Identifier: AGPL-3.0-only
// Sites-only entrypoint. Never deploy directly to a public Worker URL.
// Sites must authenticate and overwrite oai-authenticated-* at its hosting boundary.
import {handlePanelRequest,type Env} from './index';
export default {async fetch(request:Request,env:Env):Promise<Response>{
 const value=request.headers.get('oai-authenticated-user-id');
 const owner=value&&value.length<=256?value:null;
 return handlePanelRequest(request,env,owner);
}};
