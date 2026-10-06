"""Build declarative encoded I/O editions from the existing collection."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODES = {
    'makkakah': 'Sustain purpose, care, resources, useful work, and review.',
    'aantonymmakkakah': 'Reconsider framing and choose repair, revision, or release.',
    'jurisdiction': 'UNREVIEWED: identify applicable rules and appropriate review; no legal validity is certified.'
}


def build():
    records = []
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if any(part.startswith('.') or part in ('encoded', 'editions', '__pycache__') for part in relative.parts):
            continue
        if not path.is_file() or path.is_symlink() or path.name == 'publication-data.js':
            continue
        if path.suffix not in ('.md', '.html', '.js', '.css', '.py', '.cjs', '.kerot', '.json') and path.name != 'LICENSE':
            continue
        data = path.read_bytes()
        data.decode('utf-8')
        records.append({'path': relative.as_posix(), 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'encoding': 'base64', 'data': base64.b64encode(data).decode('ascii')})
    if len(records) > 500 or sum(r['bytes'] for r in records) > 5 * 1024 * 1024:
        raise ValueError('Collection exceeds reader bounds')
    folder = ROOT / 'encoded'
    folder.mkdir(exist_ok=True)
    bundles = {}
    for mode, guidance in MODES.items():
        lines = ['OSTAR_IO 1', 'EDITION ' + json.dumps({'name': mode, 'guidance': guidance}, ensure_ascii=True)]
        lines.extend('PUT ' + json.dumps(record, separators=(',', ':')) for record in records)
        lines.append('END')
        script = '\n'.join(lines) + '\n'
        if len(script.encode()) > 10 * 1024 * 1024:
            raise ValueError('Encoded script exceeds reader bounds')
        (folder / f'ostar-{mode}.io').write_text(script)
        bundles[mode] = script
    (ROOT / 'publication-data.js').write_text('globalThis.OstarEncodedEditions=' + json.dumps(bundles) + ';\n')
    print(f'Built {len(bundles)} encoded I/O editions with {len(records)} records each.')


if __name__ == '__main__':
    build()
