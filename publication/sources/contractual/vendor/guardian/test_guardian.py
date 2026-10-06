import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import guardian
import mechanics
from unittest.mock import patch


class GuardianTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_detection_and_preservation(self):
        marker = self.root / 'sample.txt'
        marker.write_bytes(guardian.EICAR)
        (self.root / 'document.locked').write_text('example')
        sha = hashlib.sha256(guardian.EICAR).hexdigest()
        report = guardian.inventory(self.root, {sha: 'test signature'})
        self.assertEqual({f['kind'] for f in report['findings']}, {'antivirus-test-file', 'known-hash', 'ransomware-name-indicator'})
        self.assertEqual(marker.read_bytes(), guardian.EICAR)
        self.assertEqual(report['errors'], [])

    def test_integrity_changes(self):
        (self.root / 'modified').write_text('original')
        (self.root / 'removed').write_text('original')
        baseline = guardian.inventory(self.root)
        (self.root / 'modified').write_text('changed')
        (self.root / 'removed').unlink()
        (self.root / 'added').write_text('new')
        self.assertEqual(guardian.compare(baseline, guardian.inventory(self.root)), {'added': ['added'], 'removed': ['removed'], 'modified': ['modified']})

    def test_symlink_not_followed(self):
        (self.root / 'link').symlink_to('/etc/passwd')
        self.assertEqual(guardian.inventory(self.root)['files'], {})

    def test_marker_across_chunk_boundary(self):
        (self.root / 'sample').write_bytes(b'a' * (1024 * 1024 - 10) + guardian.EICAR)
        self.assertEqual(len(guardian.inventory(self.root)['findings']), 1)

    def test_cli_baseline_check_and_exit_codes(self):
        baseline = self.root / 'baseline.json'
        def run(*args):
            return subprocess.run([sys.executable, guardian.__file__, *args], capture_output=True, text=True)
        args = [str(self.root), '--baseline', str(baseline)]
        self.assertEqual(run('baseline', *args).returncode, 0)
        saved = baseline.read_bytes()
        self.assertEqual(run('baseline', *args).returncode, 2)
        self.assertEqual(baseline.read_bytes(), saved)
        self.assertEqual(run('check', *args).returncode, 0)
        (self.root / 'new').write_text('new')
        result = run('check', *args)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['changes']['added'], ['new'])

    def test_invalid_signature_and_wrong_root(self):
        signatures = self.root / 'signatures.json'
        signatures.write_text('{"invalid": "bad"}')
        with self.assertRaises(ValueError):
            guardian.load_signatures(signatures)
        baseline = guardian.inventory(self.root)
        baseline['root'] = '/different'
        with self.assertRaises(ValueError):
            guardian.compare(baseline, guardian.inventory(self.root))

    def test_executable_masquerading(self):
        (self.root / 'invoice.pdf.exe').write_bytes(b'MZ' + b'fixture')
        report = guardian.inventory(self.root)
        self.assertEqual(report['findings'][0]['kind'], 'executable-masquerading')
        self.assertEqual(report['summary']['review_priority'], 'high')

    def test_script_composites_require_both_primitives(self):
        (self.root / 'download.ps1').write_text('# fixture: Invoke-WebRequest')
        self.assertEqual(guardian.inventory(self.root)['findings'], [])
        (self.root / 'download.ps1').write_text('# fixture: Invoke-WebRequest Invoke-Expression')
        self.assertEqual(guardian.inventory(self.root)['findings'][0]['kind'], 'download-and-execution-text')
        (self.root / 'capture.py').write_text('# fixture: pynput.keyboard requests.post(')
        self.assertIn('keyboard-capture-and-send-text', {f['kind'] for f in guardian.inventory(self.root)['findings']})

    def test_entropy_alone_is_not_an_alert(self):
        data = bytes(range(256)) * 256
        (self.root / 'archive.bin').write_bytes(data)
        report = guardian.inventory(self.root)
        self.assertEqual(report['files']['archive.bin']['entropy'], 8.0)
        self.assertEqual(report['findings'], [])
        (self.root / 'archive.bin').rename(self.root / 'archive.locked')
        self.assertIn('possible-encrypted-ransomware-output', {f['kind'] for f in guardian.inventory(self.root)['findings']})

    def test_encryption_change_composites(self):
        for n in range(10):
            (self.root / str(n)).write_bytes(b'a' * 65536)
        baseline = guardian.inventory(self.root)
        for n in range(10):
            (self.root / str(n)).write_bytes(bytes(range(256)) * 256)
        current = guardian.inventory(self.root)
        changes = guardian.compare(baseline, current)
        alerts = mechanics.correlate(baseline, current, changes)
        kinds = [item['kind'] for item in alerts]
        self.assertEqual(kinds.count('possible-encryption-change'), 10)
        self.assertIn('widespread-possible-encryption', kinds)
        self.assertIn('widespread-file-change', kinds)
        self.assertNotIn('widespread-file-change', [f['kind'] for f in mechanics.correlate(baseline, current, changes, 20)])

    def test_incomplete_scan_suppresses_correlations(self):
        baseline = guardian.inventory(self.root)
        current = guardian.inventory(self.root)
        current['errors'].append({'path': 'unreadable', 'error': 'denied'})
        self.assertEqual(mechanics.correlate(baseline, current, {'modified': [], 'removed': []}), [])
        self.assertFalse(mechanics.summarize(current)['complete'])

    def test_legacy_baseline_uses_content_not_new_metadata(self):
        (self.root / 'file').write_text('example')
        current = guardian.inventory(self.root)
        baseline = {'version': 1, 'root': current['root'], 'files': {
            'file': {k: current['files']['file'][k] for k in ('sha256', 'size')}}}
        self.assertEqual(guardian.compare(baseline, current)['modified'], [])

    def test_prefix_memory_is_bounded(self):
        (self.root / 'large').write_bytes(b'a' * (2 * 1024 * 1024))
        self.assertEqual(guardian.inventory(self.root)['files']['large']['sample_bytes'], mechanics.SAMPLE_LIMIT)

    def test_read_error_is_reported_and_baseline_not_saved(self):
        (self.root / 'unreadable').write_text('fixture')
        with patch('guardian.os.open', side_effect=PermissionError('denied')):
            report = guardian.inventory(self.root)
            self.assertEqual(len(report['errors']), 1)
            self.assertFalse(report['summary']['complete'])
            baseline = self.root / 'baseline.json'
            self.assertEqual(guardian.main(['baseline', str(self.root), '--baseline', str(baseline)]), 2)
            self.assertFalse(baseline.exists())


if __name__ == '__main__':
    unittest.main()
