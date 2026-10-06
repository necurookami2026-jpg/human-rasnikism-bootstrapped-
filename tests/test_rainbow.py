import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.rainbow import C, SAMPLES, frequency, record

class RainbowTests(unittest.TestCase):
    def test_physical_conversion_and_exact_roundtrips(self):
        self.assertEqual(frequency(700), Fraction(2997924580000000, 7))
        self.assertEqual(frequency('0.5'), 599584916000000000)
        previous = 0
        for colour, nm in SAMPLES:
            hz = frequency(nm)
            self.assertEqual(hz * Fraction(nm, 10**9), C)
            self.assertEqual(Fraction(C * 10**9, 1) / hz, nm)
            self.assertGreater(hz, previous)
            previous = hz
        self.assertEqual(len(record()['samples']), 7)

    def test_invalid_wavelengths(self):
        for value in (0, -1, 'nonsense'):
            with self.assertRaises(ValueError):
                frequency(value)

    def test_output_is_parseable_and_preserves_existing_record(self):
        script = Path(__file__).resolve().parents[1] / 'tools/rainbow.py'
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'observations.json'
            command = [sys.executable, str(script), '--output', str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes()
            self.assertEqual(json.loads(before), record())
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), before)
