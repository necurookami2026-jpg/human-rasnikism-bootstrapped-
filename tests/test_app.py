import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from madrigal_lab.app import main

class AppTests(unittest.TestCase):
 def test_cli_world_and_failure(self):
  with tempfile.TemporaryDirectory() as temp:
   source=Path(temp)/'world';source.write_text('world "CLI test"\ntick 1\n')
   output=io.StringIO()
   with contextlib.redirect_stdout(output):self.assertEqual(main(['--state',temp,'run',str(source)]),0)
   self.assertIn('quilt_sha256',output.getvalue())
   with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(main(['--state',temp,'action','unknown']),2)
 def test_cli_catalogue(self):
  output=io.StringIO()
  with contextlib.redirect_stdout(output):self.assertEqual(main(['catalogue']),0)
  self.assertIn('parallel_editions',output.getvalue())
