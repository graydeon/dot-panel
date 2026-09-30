#!/usr/bin/env python3
"""Build/validate a deterministic skills-based Dot Panel plugin; never install or publish."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tarfile
import zipfile
import xml.etree.ElementTree as ET
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '55b19217d08f33c01e18b51609d1685212aa1c67'
SKILLS = ('setup-dot-panel','maintain-dot-panel','create-dot-panel-widget','edit-dot-panel-widget','manage-dot-panel-usage')
SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
DENIED = {'.git','.openai','.wrangler','node_modules','dist','__pycache__','.aws','.codex','usage-helper-state.json','last-good.json','config.json','status.json'}

def digest(data): return hashlib.sha256(data).hexdigest()
def dump(value): return (json.dumps(value, indent=2, ensure_ascii=False)+'\n').encode()
def safe(path):
    p=PurePosixPath(path)
    assert path and not path.startswith('/') and '\\' not in path and ':' not in path, f'Unsafe path: {path}'
    assert all(part not in ('','.','..') for part in path.split('/')), f'Unsafe path: {path}'
    assert not any(part in DENIED for part in p.parts), f'Excluded content: {path}'
    return p

def build(output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'packaging/plugin.json').read_text())
    payload={}
    source=subprocess.check_output(['git','archive','--format=tar',SOURCE],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(source)) as archive:
        for entry in archive:
            if entry.isdir():continue
            assert entry.isfile(), f'Non-regular retained source: {entry.name}'
            safe(entry.name)
            payload['assets/framework/'+entry.name]=archive.extractfile(entry).read()
    for name in SKILLS:
        original=payload['assets/framework/agent-skills/'+name+'/SKILL.md'].decode()
        original=original.replace('../../docs/', '../../assets/framework/docs/')
        original=original.replace('`../README.md`','`../../assets/framework/agent-skills/README.md`')
        original=original.replace('`../template/`','`../../assets/framework/agent-skills/template/`')
        original+='\n## Packaged resources\n\nThe reviewed reusable source is at `../../assets/framework/` relative to this skill directory. Read the plugin root `PROVENANCE.json` and verify the retained source manifest before copying it into the requesting owner’s private installation checkout. This packaged template is a starting point; preserve newer installation-specific source and private manifests. Never deploy from or modify another owner’s retained source.\n'
        if name=='manage-dot-panel-usage':
            original+='\nThe same reviewed helper is also bundled at `scripts/usage-tracker.py` in this skill directory. Run or copy it only on the owner’s authorized local computer with the required existing CLI connection; use a dedicated private state directory outside the plugin/source. Installing this skill launches nothing.\n'
            payload['skills/'+name+'/scripts/usage-tracker.py']=payload['assets/framework/scripts/usage-tracker.py']
        payload['skills/'+name+'/SKILL.md']=original.encode()
    payload['plugin.json']=dump(manifest)
    compatibility={k:v for k,v in manifest.items() if k not in ('$schema','extensions')}
    compatibility['skills']='./skills/'
    compatibility['interface']=manifest['extensions']['com.openai']['interface']
    compatibility['extensions']={'com.openai':{'onboardingSkill':'./skills/setup-dot-panel/SKILL.md'}}
    payload['.codex-plugin/plugin.json']=dump(compatibility)
    payload['assets/icon.png']=payload['assets/framework/public/brand/favicon-180.png']
    payload['assets/header.svg']=payload['assets/framework/docs/assets/header.svg']
    for name in ('LICENSE','ASSET-LICENSE.md','THIRD_PARTY_NOTICES.md'):
        if 'assets/framework/'+name in payload:payload[name]=payload['assets/framework/'+name]
    payload['INSTALL.md']=(ROOT/'packaging/INSTALL.md').read_bytes()
    payload['PRIVACY.md']=(ROOT/'docs/privacy.md').read_bytes()
    payload['PROVENANCE.json']=dump({'package':'dot-panel','version':manifest['version'],
        'framework_commit':SOURCE,'framework_repository':manifest['repository'],
        'framework_source_manifest_sha256':digest(payload['assets/framework/SOURCE_MANIFEST.json']),
        'portable_schema':SCHEMA,'publisher_metadata_basis':'Verified public GitHub handle graydeon; portal verified identity not asserted',
        'catalog_status':'Not submitted, approved or published','native_background_runtime':'Not established; optional owner-run local helper'})
    payload['PACKAGE_CONTENTS.json']=dump({'files':[{'path':name,'sha256':digest(data)} for name,data in sorted(payload.items())]})
    path=output/('dot-panel-'+manifest['version']+'.zip')
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(payload.items()):
            safe(name);item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.create_system=3
            item.external_attr=(stat.S_IFREG|0o644)<<16;item.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(item,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return path

def validate(path, extract=None):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist();assert len(names)==len(set(names)), 'Duplicate archive entries'
        assert 'plugin.json' in names, 'Manifest must be at ZIP root'
        assert archive.testzip() is None, 'Corrupt ZIP'
        payload={}
        for item in archive.infolist():
            safe(item.filename)
            assert stat.S_IFMT(item.external_attr>>16)==stat.S_IFREG, 'Link or non-regular ZIP entry'
            assert item.file_size<8_000_000, 'Unexpected large file'
            payload[item.filename]=archive.read(item)
    m=json.loads(payload['plugin.json']);schema=json.loads((ROOT/'packaging/plugin.schema.json').read_text())
    jsonschema.Draft202012Validator(schema).validate(m)
    assert m['name']=='dot-panel' and re.fullmatch(r'\d+\.\d+\.\d+(?:-rc\.\d+)?',m['version'])
    assert m['license']=='AGPL-3.0-only'
    interface=m['extensions']['com.openai']['interface']
    for key,limit in {'displayName':30,'shortDescription':30,'longDescription':4000,'developerName':80}.items():
        assert isinstance(interface[key],str) and 0<len(interface[key])<=limit, key
    assert interface['category']=='Productivity'
    assert len(interface['defaultPrompt'])<=3 and all(0<len(v)<=128 and '@' not in v for v in interface['defaultPrompt'])
    assert not any(n in payload for n in ('mcp.json','.mcp.json','.app.json')), 'No shared connection belongs in installer'
    assert not any(k in m['extensions']['com.openai'] for k in ('apps','hooks','mcpServers'))
    for key in ('composerIcon','logo'):
        value=interface[key];assert value.startswith('./') and value[2:] in payload
    for key in ('websiteURL','supportURL','privacyPolicyURL'):
        assert interface[key].startswith('https://github.com/graydeon/dot-panel') and len(interface[key])<=1024
    assert interface['developerName']==m['author']['name']=='graydeon'
    assert m['extensions']['com.openai']['onboardingSkill']=='./skills/setup-dot-panel/SKILL.md'
    legacy=json.loads(payload['.codex-plugin/plugin.json'])
    assert legacy['name']==m['name'] and legacy['version']==m['version'] and legacy['skills']=='./skills/'
    assert {PurePosixPath(n).parts[1] for n in payload if n.startswith('skills/') and n.endswith('/SKILL.md')}==set(SKILLS)
    for name in SKILLS:
        location=PurePosixPath('skills',name,'SKILL.md');text=payload[str(location)].decode()
        assert text.startswith('---\nname: '+name+'\n') and 'description: ' in text
        refs=re.findall(r'\]\(([^)]+)\)',text)+re.findall(r'`([^`]+)`',text)
        for target in refs:
            if not target.startswith(('../','./','scripts/')):continue
            # Resolve packaged resource references without allowing them to escape ZIP root.
            parts=list(location.parent.parts)
            for part in PurePosixPath(target.split('#')[0]).parts:
                if part=='..':assert parts;parts.pop()
                elif part!='.':parts.append(part)
            normalized='/'.join(parts).rstrip('/')
            assert normalized in payload or any(n.startswith(normalized+'/') for n in payload), (name,target)
    source_manifest=json.loads(payload['assets/framework/SOURCE_MANIFEST.json'])
    for row in source_manifest['files']:
        assert digest(payload['assets/framework/'+row['path']])==row['sha256'], row['path']
    required=('package.json','package-lock.json','worker/sites.ts','scripts/build-sites.mjs','LICENSE','tests/test_usage_tracker.py')
    for name in required:assert 'assets/framework/'+name in payload
    assert payload['skills/manage-dot-panel-usage/scripts/usage-tracker.py']==payload['assets/framework/scripts/usage-tracker.py']
    assert len(payload['assets/icon.png'])<5*1024*1024 and payload['assets/icon.png'].startswith(b'\x89PNG\r\n\x1a\n')
    import struct
    width,height=struct.unpack('>II',payload['assets/icon.png'][16:24]);assert width==height and 48<=width<=4096
    ET.fromstring(payload['assets/header.svg'])
    contents=json.loads(payload['PACKAGE_CONTENTS.json'])['files'];assert {r['path'] for r in contents}==set(payload)-{'PACKAGE_CONTENTS.json'}
    for row in contents:assert digest(payload[row['path']])==row['sha256']
    private=re.compile(r'/home/gray|gradientPC|libfile_[a-z0-9]+|file_[0-9a-f]{20,}|plugin_asdk_app_[0-9a-f]+|https://[^\s"<>]*(?:sites\.chatgpt\.com|\.workers\.dev)|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for name,data in payload.items():
        if PurePosixPath(name).suffix not in ('.png','.jpg','.jpeg','.webp','.ico'):
            assert not private.search(data.decode('utf-8')), 'Private identifier/credential pattern: '+name
    if extract:
        extract=extract.resolve();assert not extract.exists(), 'Extract only into a fresh directory'
        for name,data in payload.items():
            dest=extract/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    return {'version':m['version'],'framework_commit':SOURCE,'zip_sha256':digest(path.read_bytes()),
        'zip_bytes':path.stat().st_size,'files':len(payload),'skills':list(SKILLS),
        'portable_schema_sha256':digest((ROOT/'packaging/plugin.schema.json').read_bytes()),
        'checks':['published portable schema','listing field limits','regular safe unique ZIP paths','skill/resource links','source manifest hashes','complete template','helper equality','square original PNG','privacy pattern scan'],
        'platform_acceptance':'Not tested; package checks do not establish directory acceptance'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--validate',type=Path);p.add_argument('--extract',type=Path);a=p.parse_args()
    if not a.output and not a.validate:p.error('--output or --validate required')
    path=a.validate or build(a.output)
    result=validate(path,a.extract)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
