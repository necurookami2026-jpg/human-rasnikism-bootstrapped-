"""Source-backed K0 construction tools. Guest code never invokes host eval."""
import hashlib
import importlib.util
import json
import shlex
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'vendor' / 'rasnikism'
spec = importlib.util.spec_from_file_location('lab_kerot', VENDOR / 'software' / 'kerot.py')
k0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k0)
MANIFEST = json.loads((VENDOR / 'language' / 'quilt-manifest.json').read_text())
ALIASES = {'makkah': 'makkakah', 'counterantonymmakkakah': 'counterantonymmakkkah',
           'counteraantonymmakkakah': 'counterantonymmakkkah'}


def source_text(source):
    if not isinstance(source, str) or len(source.encode('utf-8')) > 65536:
        raise ValueError('Source must be UTF-8 text of at most 64 KiB')
    return source


def assemble(source):
    return k0.assemble(source_text(source))


def disassemble(program):
    if not isinstance(program, bytes) or len(program) % 8 or len(program) > 65536:
        raise ValueError('Bytecode must contain complete eight-byte instructions')
    names = {v: k for k, v in k0.OPS.items()}
    lines = []
    for offset in range(0, len(program), 8):
        op, reg, a, b, c = struct.unpack('<BBHHH', program[offset:offset+8])
        if op not in names or reg > 15 or c or (op in (1, 2, 3, 5) and b) or (op == 5 and reg) or (op == 6 and b not in (0, 1)):
            raise ValueError(f'Invalid reserved field or opcode at byte {offset}')
        if op == 5:
            lines.append(f'step {a}')
        elif op in (4, 6):
            lines.append(f'{names[op]} r{reg}, {a}, {b}')
        else:
            lines.append(f'{names[op]} r{reg}, {a}')
    return '\n'.join(lines) + ('\n' if lines else '')


def format_source(source):
    """Canonical numeric assembly; resolves labels and drops comments."""
    return disassemble(assemble(source))


def compile_script(source):
    """Tiny Ras script: emit quoted text, exact BIT BIT, halt; no hidden IO."""
    lines = []
    halted = False
    for number, raw in enumerate(source_text(source).splitlines(), 1):
        tokens = shlex.split(raw, comments=True)
        if not tokens:
            continue
        if halted:
            raise ValueError(f'line {number}: statement after halt')
        if tokens[0] == 'emit' and len(tokens) == 2:
            data = tokens[1].encode('utf-8')
        elif tokens[0] == 'exact' and len(tokens) == 3 and all(x in ('0', '1') for x in tokens[1:]):
            data = str(int(tokens[1])+int(tokens[2])).encode()
        elif tokens == ['halt']:
            data = b''
            halted = True
            lines.append('signal r0, 2, 1')
        else:
            raise ValueError(f'line {number}: expected emit "text", exact BIT BIT, or halt')
        for byte in data:
            lines.extend([f'mark r0, {byte}', 'signal r0, 0, 1'])
    if not halted:
        lines.append('signal r0, 2, 1')
    result = '\n'.join(lines) + '\n'
    assemble(result)
    return result


def run(source, input_bytes=b'', budget=10000):
    if type(budget) is not int or not 1 <= budget <= 100000:
        raise ValueError('Instruction budget must be 1..100000')
    if not isinstance(input_bytes, bytes) or len(input_bytes) > 65536:
        raise ValueError('Input must be at most 64 KiB')
    program = assemble(source)
    machine = k0.Machine(program, input_bytes)
    status = machine.run(budget)
    return {'status': status, 'output': machine.output.decode('utf-8', errors='replace'),
            'output_hex': machine.output.hex(), 'steps': machine.steps,
            'pc': machine.pc, 'error': machine.error, 'program_sha256': hashlib.sha256(program).hexdigest()}


def quilt(mode, values):
    requested = mode
    mode = ALIASES.get(mode, mode)
    record = next((m for m in MANIFEST['modes'] if m['name'] == mode), None)
    if record is None:
        raise ValueError('Unknown quilt mode')
    if not isinstance(values, list) or len(values) != len(record['payload']) or any(type(v) is not int or v not in (0, 1) for v in values):
        raise ValueError('Supply 0/1 values for ' + ', '.join(record['payload']))
    program = (VENDOR / 'language' / MANIFEST['binary']).read_bytes()
    if hashlib.sha256(program).hexdigest() != MANIFEST['binary_sha256']:
        raise ValueError('Quilt integrity mismatch')
    code = record['code']
    machine = k0.Machine(program, bytes([(code >> 2) & 1, (code >> 1) & 1, code & 1]+values))
    status = machine.run(10000)
    return {'requested_mode': requested, 'mode': mode, 'payload_fields': record['payload'],
            'status': status, 'output': machine.output.decode('utf-8'), 'steps': machine.steps,
            'scope': record['scope'], 'inputs_are_assertions': True}
