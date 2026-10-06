"""Package every supplied K0 example for offline source reinterpretation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build():
    programs = []
    for path in sorted((ROOT / 'software/examples').glob('*.kerot')):
        programs.append({
            'id': path.stem, 'name': path.stem,
            'source': path.read_text(),
            'input': [65] if path.stem == 'echo' else [],
            'drivers': ['queue', 'latch', 'clock', 'eventlog'] if path.stem == 'drivers' else [],
            'path': path.relative_to(ROOT).as_posix(),
        })
    (ROOT / 'program-library.js').write_text(
        'globalThis.KerotProgramLibrary=' + json.dumps(programs) + ';\n')
    print(f'Packaged {len(programs)} editable Kerot examples.')


if __name__ == '__main__':
    build()
