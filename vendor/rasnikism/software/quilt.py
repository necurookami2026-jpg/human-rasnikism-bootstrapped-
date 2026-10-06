"""Run the actual primitive-only final quilt with a named Boolean payload."""
import argparse
import hashlib
import json
from pathlib import Path
from kerot import Machine

FOLDER = Path(__file__).resolve().parent.parent / 'language'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True)
    parser.add_argument('--values', type=int, nargs='*', default=[])
    args = parser.parse_args()
    manifest = json.loads((FOLDER / 'quilt-manifest.json').read_text())
    mode = next((m for m in manifest['modes'] if m['name'] == args.mode), None)
    if mode is None:
        parser.error('Choose: ' + ', '.join(m['name'] for m in manifest['modes']))
    if len(args.values) != len(mode['payload']) or any(v not in (0, 1) for v in args.values):
        parser.error('Supply Boolean 0/1 values for: ' + ', '.join(mode['payload']))
    binary = (FOLDER / manifest['binary']).read_bytes()
    if hashlib.sha256(binary).hexdigest() != manifest['binary_sha256']:
        raise SystemExit('Binary integrity mismatch; rebuild and check the edition')
    code = mode['code']
    inputs = bytes([(code >> 2) & 1, (code >> 1) & 1, code & 1] + args.values)
    machine = Machine(binary, inputs)
    result = machine.run(10000)
    if result != 'halted':
        raise SystemExit(f'Quilt did not halt: {result}; {machine.error}')
    print(machine.output.decode('utf-8'), end='')


if __name__ == '__main__':
    main()
