// SPDX-License-Identifier: AGPL-3.0-only
import {build} from 'esbuild';
import {mkdtemp,rm,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
const directory=await mkdtemp(join(tmpdir(),'dot-panel-tests-'));
try{const result=await build({entryPoints:['tests/verify.ts'],bundle:true,platform:'node',format:'esm',alias:{'cloudflare:workers':resolve('tests/binding.ts')},write:false});const file=join(directory,'verify.mjs');await writeFile(file,result.outputFiles[0].text);const run=spawnSync(process.execPath,[file],{stdio:'inherit'});process.exitCode=run.status??1;}finally{await rm(directory,{recursive:true,force:true});}
