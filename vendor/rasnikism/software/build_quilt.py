"""Build the primitive-only Ostar final-quilt program and checked binary."""
import hashlib
import json
from pathlib import Path
from kerot import assemble

ROOT = Path(__file__).resolve().parent.parent
MODES = [
    ('exact-science', ['first_bit', 'second_bit'], 'Exact addition of two Boolean bits; output is 0, 1, or 2.'),
    ('sakety', ['consent', 'readiness', 'resources'], 'Record a planning gate; not a safety certification.'),
    ('asakety', ['reconsideration', 'independent_check'], 'Record whether a review has both supplied conditions.'),
    ('sake', ['purpose_present'], 'Record whether a purpose was supplied.'),
    ('asake', ['alternative_requested'], 'Choose a reconsideration or continuation record.'),
    ('makkakah', ['resource_available'], 'Record a bounded care decision; no real-world action occurs.'),
    ('aantonymmakkakah', ['reframe_requested', 'permission_present'], 'Record a reframing decision.'),
    ('counterantonymmakkkah', ['reversal_requested', 'original_useful'], 'Reconsider a reversal while preserving useful work.')
]


def build():
    lines = ['; Ostar Rawful Lair final quilt — K0 primitive programming-language edition',
             '; Three input bytes select a mode as Boolean bits, most significant first.',
             '; Payload bytes are Boolean: zero is false, any nonzero byte is true.',
             '; Finite planning decisions, not universal safety or scientific certification.']

    def emit(line):
        lines.append(line)

    def output(label, message):
        emit(label + ':')
        for byte in (message + '\n').encode('utf-8'):
            emit(f'mark r14 {byte}')
            emit('signal r14 0 1')
        emit('signal r14 2 1')

    for register in range(3):
        emit(f'signal r{register} 1 0')
        emit(f'write r{register} {60000 + register}')
    emit('choose r0 select_0 select_1')
    for first in range(2):
        emit(f'select_{first}: choose r1 select_{first}0 select_{first}1')
        for second in range(2):
            n = first * 4 + second * 2
            emit(f'select_{first}{second}: choose r2 mode_{n} mode_{n + 1}')

    for mode, (_, fields, _) in enumerate(MODES):
        emit(f'mode_{mode}: mark r15 {mode}')
        emit('write r15 60003')
        for i in range(len(fields)):
            emit(f'signal r{i + 3} 1 0')
            emit(f'write r{i + 3} {60010 + i}')
        if mode == 0:
            emit('choose r3 add_zero add_one')
            emit('add_zero: choose r4 sum_0 sum_1')
            emit('add_one: choose r4 sum_1 sum_2')
            for number in range(3):
                output(f'sum_{number}', str(number))
        elif mode in (1, 2):
            for i in range(len(fields)):
                target = f'gate_{mode}_{i + 1}' if i + 1 < len(fields) else f'pass_{mode}'
                emit(f'gate_{mode}_{i}: choose r{i + 3} review_{mode} {target}')
            output(f'pass_{mode}', 'PLANNING CONDITIONS RECORDED' if mode == 1 else 'REVIEW CONDITIONS RECORDED')
            output(f'review_{mode}', 'REVIEW REQUIRED')
        elif mode in (3, 4, 5):
            emit(f'choose r3 false_{mode} true_{mode}')
            messages = {3: ('PURPOSE NOT SET', 'PURPOSE SET'),
                        4: ('CONTINUE REVIEW', 'RECONSIDER PURPOSE'),
                        5: ('CARE NEEDS RESOURCE', 'CARE DECISION RECORDED')}
            output(f'false_{mode}', messages[mode][0])
            output(f'true_{mode}', messages[mode][1])
        elif mode == 6:
            emit('choose r3 no_reframe check_permission')
            emit('check_permission: choose r4 reframe_review reframe_record')
            output('no_reframe', 'NO REFRAME REQUESTED')
            output('reframe_review', 'PERMISSION REVIEW REQUIRED')
            output('reframe_record', 'REFRAME DECISION RECORDED')
        else:
            emit('choose r3 no_reversal check_original')
            emit('check_original: choose r4 reversal_review preserve_original')
            output('no_reversal', 'NO REVERSAL REQUESTED')
            output('reversal_review', 'REVIEW REVERSAL')
            output('preserve_original', 'PRESERVE USEFUL WORK')

    source = '\n'.join(lines) + '\n'
    binary = assemble(source)
    if len(binary) >= 60000:
        raise ValueError('Program overlaps its trace memory')
    folder = ROOT / 'language'
    folder.mkdir(exist_ok=True)
    (folder / 'ostar-final-quilt.kerot').write_text(source)
    (folder / 'ostar-final-quilt.k0').write_bytes(binary)
    manifest = {'format': 'ostar-kerot-quilt', 'version': 1,
                'source': 'ostar-final-quilt.kerot', 'binary': 'ostar-final-quilt.k0',
                'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                'binary_sha256': hashlib.sha256(binary).hexdigest(),
                'binary_bytes': len(binary), 'host': 'Python 3 K0 reference interpreter',
                'input': '3 Boolean mode bytes, then the selected mode payload; 0 false, nonzero true',
                'scope': 'Finite Boolean computation and decision records; no domain certification.',
                'trace_memory': {'mode_bits': [60000, 60001, 60002], 'selected_mode': 60003,
                                 'payload_start': 60010},
                'modes': [{'code': i, 'name': name, 'payload': fields, 'scope': scope}
                          for i, (name, fields, scope) in enumerate(MODES)]}
    (folder / 'quilt-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (folder / 'quilt-program.js').write_text('globalThis.OstarQuiltProgram=' +
                                           json.dumps({'source': source, 'manifest': manifest}) + ';\n')
    print(f'Built executable K0 quilt: {len(binary)} bytes, {len(MODES)} modes.')


if __name__ == '__main__':
    build()
