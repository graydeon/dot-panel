// SPDX-License-Identifier: AGPL-3.0-only
// Builds the Sites-only runtime. This does not register or deploy a Site.
import {spawnSync} from 'node:child_process';
import {build} from 'esbuild';
import {rmSync} from 'node:fs';
const check=spawnSync('npx',['tsc','--noEmit'],{stdio:'inherit'});if(check.status!==0)process.exit(check.status??1);
rmSync('dist',{recursive:true,force:true});
const client=spawnSync('npx',['vite','build','--outDir','dist/client'],{stdio:'inherit'});if(client.status!==0)process.exit(client.status??1);
await build({entryPoints:['worker/sites.ts'],bundle:true,platform:'neutral',format:'esm',external:['cloudflare:workers'],outfile:'dist/server/index.js'});
console.log('Sites-only client and Worker built. Hosting manifest, private registration and native deployment are separate.');
