"""Check release documentation links, graphics and source integrity."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'SOURCE_MANIFEST.json').read_text())
for item in manifest['files']:
    path = root / item['path']
    assert path.is_file(), item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], item['path']
for path in [root / 'README.md', *root.joinpath('docs').rglob('*.md')]:
    text = path.read_text()
    links = re.findall(r'\]\(([^)]+)\)', text) + re.findall(r'src="([^"]+)"', text)
    for target in links:
        if target.startswith(('https://', 'http://', '#')):
            continue
        local = unquote(target.split('#')[0])
        assert (path.parent / local).exists(), f'{path.relative_to(root)}: {target}'
for path in root.joinpath('docs/assets').glob('*.svg'):
    ET.parse(path)
assert manifest['license'] == 'AGPL-3.0-only'
print('Documentation links, SVGs, license and source hashes passed.')
