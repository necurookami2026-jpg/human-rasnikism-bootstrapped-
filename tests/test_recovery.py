import base64
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from madrigal_lab import recovery
from madrigal_lab.runtime import Runtime


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Runtime(Path(self.temp.name) / 'state')
        self.content = 'Owner backup: care 🌿\n'
        self.digest = hashlib.sha256(self.content.encode()).hexdigest()

    def record(self, **changes):
        record = {'backup': self.content, 'owner_asserted': True,
                  'expected_sha256': self.digest, 'target': 'restored/note.txt'}
        record.update(changes)
        return record

    def test_case_specific_plans_never_claim_account_restored(self):
        results = {case: recovery.plan({'case': case, 'owner_asserted': True,
                    'provider': 'Example provider', 'official_url': 'https://example.com/support'})
                   for case in recovery.CASES}
        self.assertIn('Forgot password', ' '.join(results['forgotten-password']['steps']))
        self.assertIn('individual contact block', ' '.join(results['blocked']['steps']))
        self.assertIn('reopening', ' '.join(results['closed']['steps']))
        self.assertIn('suspension notice', ' '.join(results['suspended']['steps']))
        for result in results.values():
            self.assertFalse(result['account_restored'])
            self.assertEqual(result['remote_actions'], 0)
            self.assertIn('provider', result['provider_decision'])
            self.assertEqual(result['url_status'], 'user-supplied; not fetched or verified')

    def test_plans_reject_credentials_unknown_fields_and_nonowners(self):
        base = {'case': 'blocked', 'owner_asserted': True}
        bad = [None, [], dict(base, password='secret'), dict(base, case='universal-unblock'),
               dict(base, owner_asserted=1), dict(base, owner_asserted='true'),
               dict(base, provider=''), dict(base, provider=42)]
        bad.extend(dict(base, official_url=url) for url in (
            'http://example.com', 'https://user:secret@example.com',
            'https://example.com#token', 'https://example.com:bogus',
            'https://exa mple.com', None))
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                recovery.plan(value)

    def test_encoding_roundtrips_utf8_without_cryptographic_claims(self):
        raw = self.content.encode('utf-8')
        for encoding, payload in [('utf8', self.content), ('hex', raw.hex()),
                                  ('base64', base64.b64encode(raw).decode())]:
            result = recovery.decode(payload, encoding)
            self.assertEqual(result['text'], self.content)
            self.assertEqual(result['sha256'], self.digest)
            self.assertEqual(result['bytes'], len(raw))
            self.assertFalse(result['cryptographic_decryption'])

    def test_vault_envelopes_are_bounded_encoding_containers(self):
        payload = self.content
        encoding = 'utf8'
        for _ in range(8):
            payload = json.dumps({'encoding': encoding, 'payload': payload})
            encoding = 'vault-json'
        result = recovery.decode(payload, encoding)
        self.assertEqual(result['text'], self.content)
        self.assertEqual(result['layers'], ['vault-json'] * 8 + ['utf8'])
        ninth = json.dumps({'encoding': 'vault-json', 'payload': payload})
        with self.assertRaises(ValueError):
            recovery.decode(ninth, 'vault-json')
        for value in ('[]', '{"encoding":"utf8","payload":"x","key":"secret"}',
                      '{"encoding":"utf8","encoding":"hex","payload":"x"}',
                      '{"encoding":"utf8","payload":{}}'):
            with self.assertRaises(ValueError):
                recovery.decode(value, 'vault-json')

    def test_decoder_rejects_invalid_encoding_binary_and_byte_limits(self):
        for payload, encoding in [(True, 'utf8'), ('x', 'decrypt'), ('x', []),
                                  ('0', 'hex'), ('61 62', 'hex'), ('ff', 'hex'),
                                  ('@@', 'base64'), ('YQ', 'base64'), ('/w==', 'base64'),
                                  ('\ud800', 'utf8'), ('🌿' * 16385, 'utf8'),
                                  ('61' * 32769, 'hex')]:
            with self.subTest(encoding=encoding), self.assertRaises(ValueError):
                recovery.decode(payload, encoding)
        self.assertEqual(recovery.decode('x' * 65536)['bytes'], 65536)

    def test_integrity_is_separate_from_authenticity_and_ownership(self):
        bare = {'backup': self.content, 'owner_asserted': True}
        unchecked = recovery.inspect_backup(bare)
        self.assertEqual(unchecked['integrity'], 'not compared')
        mismatch = recovery.inspect_backup(dict(bare, expected_sha256='0' * 64))
        self.assertEqual(mismatch['integrity'], 'mismatch')
        matched = recovery.inspect_backup(dict(bare, expected_sha256=self.digest))
        self.assertEqual(matched['integrity'], 'matches')
        self.assertFalse(matched['authenticity_verified'])
        self.assertFalse(matched['ownership_verified'])
        for value in (dict(bare, owner_asserted=1), dict(bare, key='secret'),
                      dict(bare, expected_sha256=True), dict(bare, expected_sha256='bad')):
            with self.assertRaises(ValueError):
                recovery.inspect_backup(value)

    def test_local_restore_preserves_utf8_and_never_changes_remote_access(self):
        result = recovery.restore(self.runtime, self.record())
        self.assertEqual(self.runtime.read('restored/note.txt')['text'], self.content)
        self.assertEqual(result['sha256'], self.digest)
        self.assertEqual(result['status'], 'local-document-restored')
        self.assertFalse(result['account_restored'])
        self.assertEqual(result['remote_actions'], 0)
        self.assertEqual(os.stat(self.runtime.root / 'restored/note.txt').st_mode & 0o777, 0o600)

    def test_failed_digest_or_ownership_writes_nothing(self):
        bad = [self.record(expected_sha256='0' * 64), self.record(owner_asserted=1),
               self.record(owner_asserted=False), self.record(password='secret'),
               self.record(backup='x' * 65537)]
        missing = self.record()
        del missing['expected_sha256']
        bad.append(missing)
        for value in bad:
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, value)
            self.assertEqual(list(self.runtime.root.rglob('*')), [])

    def test_existing_files_and_path_escapes_cannot_be_overwritten(self):
        self.runtime.write('existing.txt', 'retain me')
        for target in ('existing.txt', '../escape.txt', '/tmp/escape.txt', '.hidden',
                       'nested/../escape.txt', 'nested/./escape.txt', 'nested//escape.txt',
                       'nested\\escape.txt', 'nested/'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target=target))
        self.assertEqual(self.runtime.read('existing.txt')['text'], 'retain me')
        self.assertEqual(len(self.runtime.files()), 1)

    def test_symlink_parents_and_targets_are_rejected(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        self.runtime.root.joinpath('linked').symlink_to(outside, target_is_directory=True)
        self.runtime.root.joinpath('linked-file').symlink_to(outside / 'new.txt')
        for target in ('linked/new.txt', 'linked-file'):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target=target))
        self.assertEqual(list(outside.iterdir()), [])

    def test_parent_swap_race_cannot_redirect_restore(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        parent = self.runtime.root / 'restored'
        parent.mkdir()
        original_open = os.open

        def swap_before_parent_open(path, flags, *args, **kwargs):
            if path == 'restored' and 'dir_fd' in kwargs:
                parent.rmdir()
                parent.symlink_to(outside, target_is_directory=True)
            return original_open(path, flags, *args, **kwargs)

        with patch.object(recovery.os, 'open', side_effect=swap_before_parent_open):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record())
        self.assertEqual(list(outside.iterdir()), [])

    def test_replaced_state_ancestor_symlink_cannot_redirect_restore(self):
        outside = Path(self.temp.name) / 'outside'
        outside.joinpath('files').mkdir(parents=True)
        original = Path(self.temp.name) / 'original-state'
        self.runtime.state.rename(original)
        self.runtime.state.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            recovery.restore(self.runtime, self.record(target='new.txt'))
        self.assertEqual(list(outside.joinpath('files').iterdir()), [])
        self.assertEqual(list(original.joinpath('files').iterdir()), [])

    def test_distinct_restore_calls_share_an_atomic_entry_budget(self):
        for index in range(255):
            self.runtime.write(f'existing{index}.txt', 'retain')
        other_runtime = Runtime(self.runtime.state)
        start = threading.Barrier(2)
        first_counted = threading.Event()
        release_count = threading.Event()
        counts = []
        original_count = recovery._entry_count

        def gate_count(directory, budget=257):
            count = original_count(directory, budget)
            counts.append(count)
            if len(counts) == 1:
                first_counted.set()
                if not release_count.wait(5):
                    raise AssertionError('Test did not release the first restore')
            return count

        def attempt(index):
            start.wait(timeout=5)
            try:
                runtime = self.runtime if index == 0 else other_runtime
                recovery.restore(runtime, self.record(target=f'new{index}.txt'))
                return True
            except ValueError:
                return False

        with patch.object(recovery, '_entry_count', side_effect=gate_count):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                results = [pool.submit(attempt, index) for index in range(2)]
                self.assertTrue(first_counted.wait(5))
                release_count.set()
                self.assertEqual(sum(result.result(timeout=5) for result in results), 1)
        self.assertEqual(counts, [255, 256])
        self.assertEqual(len(list(self.runtime.root.iterdir())), 256)

    def test_external_cooperating_directory_lock_prevents_partial_restore(self):
        lock = os.open(self.runtime.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record())
            self.assertEqual(list(self.runtime.root.rglob('*')), [])
        finally:
            os.close(lock)
        self.assertEqual(recovery.restore(self.runtime, self.record())['status'],
                         'local-document-restored')

    def test_failed_file_creation_removes_only_own_empty_parent_directories(self):
        kept = self.runtime.root / 'kept'
        kept.mkdir()
        original_open = os.open

        def fail_final_open(path, flags, *args, **kwargs):
            if flags & os.O_CREAT:
                raise OSError('Injected creation failure')
            return original_open(path, flags, *args, **kwargs)

        with patch.object(recovery.os, 'open', side_effect=fail_final_open):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target='kept/new/parents/note.txt'))
        self.assertTrue(kept.is_dir())
        self.assertEqual(list(kept.iterdir()), [])

    def test_failed_restore_preserves_parent_populated_by_another_writer(self):
        original_open = os.open

        def add_other_document_then_fail(path, flags, *args, **kwargs):
            if flags & os.O_CREAT:
                descriptor = original_open('someone-elses.txt', flags, 0o600,
                                           dir_fd=kwargs['dir_fd'])
                with os.fdopen(descriptor, 'w') as stream:
                    stream.write('retain this unrelated document')
                raise OSError('Injected creation failure')
            return original_open(path, flags, *args, **kwargs)

        with patch.object(recovery.os, 'open', side_effect=add_other_document_then_fail):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target='new/parents/note.txt'))
        retained = self.runtime.root / 'new/parents/someone-elses.txt'
        self.assertEqual(retained.read_text(), 'retain this unrelated document')
        self.assertFalse(self.runtime.root.joinpath('new/parents/note.txt').exists())

    def test_failed_new_parent_open_rolls_back_its_empty_directory(self):
        original_open = os.open

        def fail_new_directory_open(path, flags, *args, **kwargs):
            if path == 'new' and 'dir_fd' in kwargs and flags & os.O_DIRECTORY:
                raise OSError('Injected directory open failure')
            return original_open(path, flags, *args, **kwargs)

        with patch.object(recovery.os, 'open', side_effect=fail_new_directory_open):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target='new/note.txt'))
        self.assertEqual(list(self.runtime.root.iterdir()), [])

    def test_rollback_preserves_a_replaced_empty_parent(self):
        original_open = os.open
        replacement = self.runtime.root / 'new'
        original_parent = Path(self.temp.name) / 'moved-original-parent'

        def replace_new_parent_before_open(path, flags, *args, **kwargs):
            if path == 'new' and 'dir_fd' in kwargs and flags & os.O_DIRECTORY:
                replacement.rename(original_parent)
                replacement.mkdir()
            return original_open(path, flags, *args, **kwargs)

        with patch.object(recovery.os, 'open', side_effect=replace_new_parent_before_open):
            with self.assertRaises(ValueError):
                recovery.restore(self.runtime, self.record(target='new/note.txt'))
        self.assertTrue(replacement.is_dir())
        self.assertEqual(list(replacement.iterdir()), [])
        self.assertEqual(list(original_parent.iterdir()), [])

    def test_exclusive_concurrent_restore_and_document_count_bound(self):
        def attempt(_):
            try:
                recovery.restore(self.runtime, self.record())
                return True
            except ValueError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(attempt, range(2))), 1)
        self.assertEqual(self.runtime.read('restored/note.txt')['text'], self.content)
        for index in range(253):
            self.runtime.write(f'extra{index}.txt', 'x')
        with self.assertRaises(ValueError):
            recovery.restore(self.runtime, self.record(target='new-parent/new.txt'))
        self.assertFalse(self.runtime.root.joinpath('new-parent').exists())

    def test_functions_do_not_contact_providers_or_execute_backups(self):
        executable_text = '__import__("os").system("unexpected")'
        digest = hashlib.sha256(executable_text.encode()).hexdigest()
        with patch('socket.socket', side_effect=AssertionError('Network access forbidden')), \
                patch('subprocess.Popen', side_effect=AssertionError('Execution forbidden')):
            recovery.plan({'case': 'closed', 'owner_asserted': True,
                           'official_url': 'https://example.com/reopen'})
            result = recovery.restore(self.runtime, self.record(backup=executable_text,
                                       expected_sha256=digest))
            self.assertEqual(result['status'], 'local-document-restored')
        self.assertEqual(self.runtime.read('restored/note.txt')['text'], executable_text)


if __name__ == '__main__':
    unittest.main()
