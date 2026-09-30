// SPDX-License-Identifier: AGPL-3.0-only
export function ownerOf(r:Request){const id=r.headers.get('oai-authenticated-user-id');if(!id)throw new Error('Sign in required');return id;}
export function sameOrigin(r:Request){const origin=r.headers.get('origin');if(!origin||origin!==new URL(r.url).origin)throw new Error('Origin mismatch');}
export function failure(e:unknown){return Response.json({error:e instanceof Error?e.message:'Service unavailable'},{status:e instanceof Error&&e.message==='Sign in required'?401:409,headers:{'Cache-Control':'no-store'}});}
