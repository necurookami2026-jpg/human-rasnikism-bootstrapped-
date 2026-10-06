import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from kerot import Machine, assemble

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / 'language'


class QuiltTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((FOLDER / 'quilt-manifest.json').read_text())
        cls.binary = (FOLDER / 'ostar-final-quilt.k0').read_bytes()

    def expected(self, code, values):
        if code == 0:
            return str(sum(values)) + '\n'
        if code == 1:
            return 'PLANNING CONDITIONS RECORDED\n' if all(values) else 'REVIEW REQUIRED\n'
        if code == 2:
            return 'REVIEW CONDITIONS RECORDED\n' if all(values) else 'REVIEW REQUIRED\n'
        if code == 3:
            return 'PURPOSE SET\n' if values[0] else 'PURPOSE NOT SET\n'
        if code == 4:
            return 'RECONSIDER PURPOSE\n' if values[0] else 'CONTINUE REVIEW\n'
        if code == 5:
            return 'CARE DECISION RECORDED\n' if values[0] else 'CARE NEEDS RESOURCE\n'
        if code == 6:
            return ('NO REFRAME REQUESTED\n' if not values[0] else
                    'REFRAME DECISION RECORDED\n' if values[1] else 'PERMISSION REVIEW REQUIRED\n')
        return ('NO REVERSAL REQUESTED\n' if not values[0] else
                'PRESERVE USEFUL WORK\n' if values[1] else 'REVIEW REVERSAL\n')

    def test_source_is_actual_published_binary(self):
        source = (FOLDER / 'ostar-final-quilt.kerot').read_bytes()
        self.assertEqual(assemble(source.decode()), self.binary)
        self.assertEqual(hashlib.sha256(source).hexdigest(), self.manifest['source_sha256'])
        self.assertEqual(hashlib.sha256(self.binary).hexdigest(), self.manifest['binary_sha256'])
        self.assertLess(len(self.binary), 60000)

    def test_all_boolean_modes_and_trace(self):
        self.assertEqual(len(self.manifest['modes']), 8)
        for mode in self.manifest['modes']:
            code = mode['code']
            header = [(code >> 2) & 1, (code >> 1) & 1, code & 1]
            for values in itertools.product((0, 1), repeat=len(mode['payload'])):
                with self.subTest(mode=mode['name'], values=values):
                    machine = Machine(self.binary, bytes(header + list(values) + [99]))
                    self.assertEqual(machine.run(), 'halted')
                    self.assertEqual(machine.output.decode(), self.expected(code, values))
                    self.assertEqual(list(machine.memory[60000:60003]), header)
                    self.assertEqual(machine.memory[60003], code)
                    self.assertEqual(list(machine.memory[60010:60010 + len(values)]), list(values))
                    self.assertEqual(machine.input_offset, 3 + len(values))
                    nonzero = Machine(self.binary, bytes([255 if v else 0 for v in header + list(values)]))
                    self.assertEqual(nonzero.run(), 'halted')
                    self.assertEqual(nonzero.output, machine.output)

    def test_incomplete_input_waits_without_a_result(self):
        for mode in self.manifest['modes']:
            code = mode['code']
            complete = bytes([(code >> 2) & 1, (code >> 1) & 1, code & 1] + [1] * len(mode['payload']))
            for size in range(len(complete)):
                with self.subTest(mode=mode['name'], prefix=size):
                    machine = Machine(self.binary, complete[:size])
                    self.assertEqual(machine.run(), 'waiting')
                    self.assertEqual(machine.output, b'')
                    machine.input.extend(complete[size:])
                    self.assertEqual(machine.run(), 'halted')

    def test_runner(self):
        for mode in self.manifest['modes']:
            values = [1] * len(mode['payload'])
            result = subprocess.run([sys.executable, str(ROOT / 'software/quilt.py'),
                                     '--mode', mode['name'], '--values', *map(str, values)],
                                    capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual(result.stdout.decode(), self.expected(mode['code'], values))


if __name__ == '__main__':
    unittest.main()
