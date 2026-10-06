"""Provider-directed recovery plans and integrity-checked local backup restoration.

The encoding decoder handles user-supplied text only. It has no authentication,
cryptographic decryption, network, credential or provider-management interface.
"""
import base64
import binascii
import fcntl
import hashlib
import json
import os
import re
import stat
import threading
import urllib.parse

LIMIT = 65536
MAX_DEPTH = 8
ENCODINGS = ('utf8', 'hex', 'base64', 'vault-json')
CASES = ('forgotten-password', 'blocked', 'closed', 'suspended')
_RESTORE_LOCK = threading.RLock()
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _record(value, fields, required):
    if type(value) is not dict or not all(type(k) is str for k in value):
        raise ValueError('Expected a record with named fields')
    if set(value) - set(fields) or set(required) - set(value):
        raise ValueError('Unexpected or missing recovery fields')
    return value


def _text(value, maximum=LIMIT):
    if type(value) is not str:
        raise ValueError('Expected bounded UTF-8 text')
    try:
        data = value.encode('utf-8')
    except UnicodeError as error:
        raise ValueError('Expected valid UTF-8 text') from error
    if len(data) > maximum:
        raise ValueError('Recovery text exceeds its byte limit')
    return data


def _owner(record):
    if record.get('owner_asserted') is not True:
        raise ValueError('Explicit owner_asserted=true is required')


def _digest(value):
    if type(value) is not str or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Expected a lowercase SHA-256 digest')
    return value


def plan(record):
    """Return an unexecuted official-channel checklist for an asserted owner."""
    _record(record, ('case', 'owner_asserted', 'provider', 'official_url'),
            ('case', 'owner_asserted'))
    _owner(record)
    case = record['case']
    if type(case) is not str or case not in CASES:
        raise ValueError('Choose forgotten-password, blocked, closed or suspended')
    provider = record.get('provider', 'your account provider')
    _text(provider, 160)
    if not provider.strip():
        raise ValueError('Provider label must contain text')
    url = record.get('official_url')
    if 'official_url' in record:
        _text(url, 2048)
        try:
            parsed = urllib.parse.urlsplit(url)
            port = parsed.port
        except ValueError as error:
            raise ValueError('Supply a valid HTTPS provider link') from error
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or port not in (None, 443)
                or parsed.fragment or any(c.isspace() or ord(c) < 32 for c in url)):
            raise ValueError('Supply a HTTPS provider link without credentials or fragment')
    shared = [
        'Open the official provider website or app independently and confirm its identity.',
        'Keep passwords, recovery codes and identity documents out of this publication and its records.',
    ]
    specific = {
        'forgotten-password': [
            'Use the provider\'s Forgot password or Recover account workflow.',
            'Use a recovery contact, recovery email, passkey or previously saved recovery code only through the provider.',
            'If those methods are unavailable, request the provider\'s ownership review through official support.',
        ],
        'blocked': [
            'Read the restriction notice and identify its scope and available appeal process.',
            'Submit an ownership-based appeal through official support and wait for the provider\'s decision.',
            'An individual contact block remains that person\'s choice; do not use this checklist to evade it.',
        ],
        'closed': [
            'Check whether the provider permits reopening and whether its recovery or export window is still open.',
            'Request reopening or a permitted data export through official support.',
            'If the account or retained data cannot be recovered, use your own lawful backups for local documents.',
        ],
        'suspended': [
            'Read the suspension notice and the provider\'s stated appeal requirements.',
            'Submit the requested explanation and ownership information only through the official appeal channel.',
            'Wait for the provider\'s decision and retain the notice and appeal reference privately.',
        ],
    }
    return {
        'case': case, 'provider': provider, 'owner_asserted': True,
        'official_url': url, 'url_status': 'user-supplied; not fetched or verified' if url else 'not supplied',
        'steps': shared + specific[case], 'status': 'guidance-only',
        'provider_decision': 'pending; determined by the provider',
        'account_restored': False, 'remote_actions': 0,
    }


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate vault-envelope fields are rejected')
        result[key] = value
    return result


def _decode(payload, encoding, depth, layers):
    raw = _text(payload)
    if type(encoding) is not str or encoding not in ENCODINGS:
        raise ValueError('Choose utf8, hex, base64 or vault-json encoding')
    layers.append(encoding)
    if encoding == 'vault-json':
        if depth >= MAX_DEPTH:
            raise ValueError('Vault-envelope depth exceeds 8')
        try:
            envelope = json.loads(payload, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, RecursionError) as error:
            raise ValueError('Expected a bounded JSON encoding envelope') from error
        _record(envelope, ('encoding', 'payload'), ('encoding', 'payload'))
        return _decode(envelope['payload'], envelope['encoding'], depth + 1, layers)
    if encoding == 'utf8':
        data = raw
    elif encoding == 'hex':
        if len(payload) % 2 or not re.fullmatch(r'[0-9a-fA-F]*', payload):
            raise ValueError('Expected hexadecimal byte pairs')
        data = bytes.fromhex(payload)
    else:
        try:
            data = base64.b64decode(raw, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError('Expected strict base64 text') from error
    if len(data) > LIMIT:
        raise ValueError('Decoded document exceeds 64 KiB')
    try:
        return data.decode('utf-8'), data
    except UnicodeError as error:
        raise ValueError('Decoded document must be UTF-8 text') from error


def decode(payload, encoding='utf8'):
    """Decode encoding layers into bounded UTF-8 text, without decryption."""
    layers = []
    content, data = _decode(payload, encoding, 0, layers)
    return {'text': content, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'encoding': encoding, 'layers': layers, 'cryptographic_decryption': False}


def inspect_backup(record):
    """Calculate, or compare, the digest of an asserted owner's text backup."""
    _record(record, ('backup', 'encoding', 'owner_asserted', 'expected_sha256'),
            ('backup', 'owner_asserted'))
    _owner(record)
    expected = _digest(record['expected_sha256']) if 'expected_sha256' in record else None
    result = decode(record['backup'], record.get('encoding', 'utf8'))
    result.update(expected_sha256=expected,
                  integrity='matches' if expected == result['sha256'] else 'mismatch' if expected else 'not compared',
                  owner_asserted=True, ownership_verified=False, authenticity_verified=False)
    return result


def _open_root(root):
    """Open every absolute ancestor without following any replacement symlink."""
    if not root.is_absolute() or any(part in ('.', '..') for part in root.parts):
        raise ValueError('Runtime document root must be an absolute canonical path')
    directory = os.open('/', _DIRECTORY_FLAGS)
    try:
        for part in root.parts[1:]:
            following = os.open(part, _DIRECTORY_FLAGS, dir_fd=directory)
            os.close(directory)
            directory = following
        return directory
    except BaseException:
        os.close(directory)
        raise


def _entry_count(directory, budget=257):
    """Count through anchored descriptors, stopping after the usable budget."""
    count = 0
    with os.scandir(directory) as entries:
        for entry in entries:
            count += 1
            if count >= budget:
                return count
            info = os.stat(entry.name, dir_fd=directory, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(entry.name, _DIRECTORY_FLAGS, dir_fd=directory)
                try:
                    count += _entry_count(child, budget - count)
                finally:
                    os.close(child)
                if count >= budget:
                    return count
    return count


def _missing_entries(root, parts):
    directory = os.dup(root)
    try:
        for index, part in enumerate(parts):
            try:
                info = os.stat(part, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                return len(parts) - index
            if index == len(parts) - 1:
                raise ValueError('Restore target already exists; choose a new document path')
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError('Restore parents must be real directories')
            following = os.open(part, _DIRECTORY_FLAGS, dir_fd=directory)
            os.close(directory)
            directory = following
        return 0
    finally:
        os.close(directory)


def _rollback_directories(created):
    for parent, name, identity in reversed(created):
        try:
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if stat.S_ISDIR(current.st_mode) and (current.st_dev, current.st_ino) == identity:
                os.rmdir(name, dir_fd=parent)
        except OSError:
            # Keep any populated, replaced or otherwise unavailable directory.
            pass


def _create_document(root, parts, content):
    directory = os.dup(root)
    created = []
    succeeded = False
    try:
        for part in parts[:-1]:
            made = False
            try:
                os.mkdir(part, mode=0o700, dir_fd=directory)
                made = True
            except FileExistsError:
                pass
            identity = None
            if made:
                info = os.stat(part, dir_fd=directory, follow_symlinks=False)
                identity = (info.st_dev, info.st_ino)
                created.append((os.dup(directory), part, identity))
            following = os.open(part, _DIRECTORY_FLAGS, dir_fd=directory)
            if made:
                info = os.fstat(following)
                if (info.st_dev, info.st_ino) != identity:
                    os.close(following)
                    raise ValueError('A newly created restore parent was replaced')
            os.close(directory)
            directory = following
        filename = parts[-1]
        descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        identity = None
        wrapped = False
        try:
            identity = os.fstat(descriptor)
            stream = os.fdopen(descriptor, 'wb')
            wrapped = True
            with stream:
                stream.write(content.encode('utf-8'))
        except BaseException:
            if not wrapped:
                os.close(descriptor)
            try:
                current = os.stat(filename, dir_fd=directory, follow_symlinks=False)
                if identity is not None and (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                    os.unlink(filename, dir_fd=directory)
            except OSError:
                pass
            raise
        succeeded = True
    finally:
        os.close(directory)
        if not succeeded:
            _rollback_directories(created)
        for parent, _, _ in created:
            os.close(parent)


def restore(runtime, record):
    """Exclusively create a new local document after a required digest match."""
    _record(record, ('backup', 'encoding', 'owner_asserted', 'expected_sha256', 'target'),
            ('backup', 'owner_asserted', 'expected_sha256', 'target'))
    checked = inspect_backup({key: value for key, value in record.items() if key != 'target'})
    if checked['integrity'] != 'matches':
        raise ValueError('Backup digest does not match; no document was restored')
    relative = record['target']
    _text(relative, 512)
    parts = relative.split('/')
    if (not relative or '\\' in relative or '\x00' in relative
            or any(part in ('', '.', '..') or part.startswith('.') for part in parts)):
        raise ValueError('Use a nonempty canonical relative document path')
    # A process lock covers calls through different Runtime instances. The POSIX
    # directory lock also excludes cooperating restores from other processes.
    with _RESTORE_LOCK:
        root = None
        try:
            root = _open_root(runtime.root)
            fcntl.flock(root, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if _entry_count(root) + _missing_entries(root, parts) > 256:
                raise ValueError('Document count limit reached')
            _create_document(root, parts, checked['text'])
        except OSError as error:
            raise ValueError('Local restore could not create an exclusive document') from error
        finally:
            if root is not None:
                os.close(root)
    return {'path': relative, 'bytes': checked['bytes'], 'sha256': checked['sha256'],
            'status': 'local-document-restored',
            'integrity': 'matches', 'owner_asserted': True, 'ownership_verified': False,
            'account_restored': False, 'remote_actions': 0}
