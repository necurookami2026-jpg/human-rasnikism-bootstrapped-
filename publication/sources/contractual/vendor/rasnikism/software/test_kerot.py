import struct
import unittest
from pathlib import Path
from kerot import Machine, assemble


class KerotTests(unittest.TestCase):
    def test_encoding_and_forward_label(self):
        self.assertEqual(assemble('step end\nend: signal r0 2 1'),
                         struct.pack('<BBHHH', 5, 0, 8, 0, 0) +
                         struct.pack('<BBHHH', 6, 0, 2, 1, 0))

    def test_all_data_operations(self):
        m = Machine(assemble('mark r0 321\nwrite r0 600\nread r1 600\nsignal r1 0 1\nsignal r0 2 1'))
        self.assertEqual(m.run(), 'halted')
        self.assertEqual(m.memory[600], 65)
        self.assertEqual(m.registers[1], 65)
        self.assertEqual(m.output, b'A')

    def test_both_branches(self):
        for value, expected in ((0, b'Z'), (1, b'N')):
            m = Machine(assemble(f'mark r0 {value}\nchoose r0 zero nonzero\nzero: mark r1 90\nstep output\nnonzero: mark r1 78\noutput: signal r1 0 1\nsignal r0 2 1'))
            self.assertEqual(m.run(), 'halted')
            self.assertEqual(m.output, expected)

    def test_input_pause_and_resume(self):
        m = Machine(assemble('signal r0 1 0\nsignal r0 0 1\nsignal r0 2 1'))
        self.assertEqual(m.run(), 'waiting')
        self.assertEqual((m.pc, m.steps, m.registers[0]), (0, 0, 0))
        m.input.extend(b'Q')
        self.assertEqual(m.run(), 'halted')
        self.assertEqual(m.output, b'Q')

    def test_budget(self):
        m = Machine(assemble('loop: step loop'))
        self.assertEqual(m.run(7), 'budget-exhausted')
        self.assertEqual(m.steps, 7)

    def test_invalid_instructions_atomic(self):
        for fields in ((255, 0, 0, 0, 0), (1, 16, 0, 0, 0),
                       (1, 0, 1, 2, 0), (5, 1, 0, 0, 0),
                       (6, 0, 99, 1, 0), (6, 0, 0, 0, 0),
                       (6, 0, 0, 2, 0), (1, 0, 1, 0, 1)):
            m = Machine(struct.pack('<BBHHH', *fields))
            self.assertEqual(m.run(), 'fault')
            self.assertEqual((m.pc, m.steps, m.registers[0]), (0, 0, 0))

    def test_fetch_and_next_bounds(self):
        m = Machine(assemble('step 65535'))
        self.assertEqual(m.run(), 'fault')
        m = Machine(b'')
        m.pc = 65529
        self.assertEqual(m.run(), 'fault')
        m = Machine(b'', entry=65528)
        m.memory[65528:] = assemble('mark r0 7')
        self.assertEqual(m.run(), 'fault')
        self.assertEqual(m.registers[0], 0)

    def test_bad_source(self):
        for source in ('step missing', 'x: step x\nx: step x', 'mark r16 1',
                       'mark r0 65536', 'mark r0 -1', 'add r0 1',
                       'signal r0 0 2', 'step', 'mark nope 1'):
            with self.assertRaises(ValueError):
                assemble(source)

    def test_samples(self):
        expected = {'general': b'KEROT READY\n', 'makkakah': b'SUSTAIN CARE\n',
                    'aantonymmakkakah': b'REFRAME FOR REPAIR\n', 'echo': b'X'}
        for name, output in expected.items():
            with self.subTest(name=name):
                source = (Path(__file__).parent / 'examples' / (name + '.kerot')).read_text()
                m = Machine(assemble(source), b'X')
                self.assertEqual(m.run(), 'halted')
                self.assertEqual(m.output, output)


if __name__ == '__main__':
    unittest.main()
