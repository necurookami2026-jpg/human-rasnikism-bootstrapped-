# Owner recovery, encoding envelopes and restored documents

The recovery chamber gives an account owner a route back to the account provider and gives a local document owner a way to inspect and restore a supplied backup. These are different outcomes. A provider decides whether its account can be reopened, unblocked or recovered. The local workbench can create a new document inside its own document directory after its bytes match an expected SHA-256 digest. Every account checklist reports `account_restored: false`, and a successful local restore continues to report that value.

The requested names “password decipherer,” “universal deblock” and “vaultception decipherer” are retained as requested concepts with defined implementation boundaries. The implemented password workflow is an official recovery checklist. The implemented blocked-account workflow is an official appeal checklist. The implemented vault envelope is a bounded text encoding container. There is no password guessing, credential collection, authentication bypass, recovery-code generator or cryptographic decryption engine in this chamber. A person's decision to block contact also remains their decision.

## The account passage checklist

`madrigal_lab.recovery.plan(record)` accepts a record with `case` and `owner_asserted`. The owner assertion must be the Boolean `true`; a number or a string does not substitute for it. The assertion is recorded as an assertion and does not verify identity. An optional `provider` label may contain up to 160 UTF-8 bytes. An optional `official_url` may contain up to 2,048 UTF-8 bytes and must be a HTTPS URL without embedded credentials, a fragment or a custom port. The software displays that URL as user-supplied. It never fetches the link or establishes that the provider controls it.

The four case values lead to distinct advice. `forgotten-password` directs the owner to the provider's reset process, established recovery contacts and ownership review. `blocked` directs the owner to the restriction notice and the available appeal process, while distinguishing a provider restriction from an individual contact block. `closed` asks the owner to check reopening and permitted export windows and to use their own backups if the provider cannot return the data. `suspended` directs the owner to the suspension notice and its official appeal requirements. Each checklist asks the owner to reach the provider independently and keep passwords, recovery codes and identity documents out of the publication and workbench records.

```python
from madrigal_lab import recovery

checklist = recovery.plan({
    'case': 'forgotten-password',
    'owner_asserted': True,
    'provider': 'My account provider',
    'official_url': 'https://example.com/support',
})
assert checklist['status'] == 'guidance-only'
assert checklist['account_restored'] is False
assert checklist['remote_actions'] == 0
```

The example URL is a placeholder. The result is a plan to review, not a submitted support request. This module has no remote account connection and sends no appeal, email or recovery request. A provider can refuse an appeal or have no reopening mechanism. The checklist preserves that uncertainty in `provider_decision` rather than translating a review into access.

## The local vault envelope

`recovery.decode(payload, encoding='utf8')` accepts a user-supplied string and one of four exact encoding names: `utf8`, `hex`, `base64` or `vault-json`. UTF-8 retains plain text. Hexadecimal requires complete byte pairs without spaces. Base64 requires its strict alphabet and padding. Every decoded document must be valid UTF-8. The input at every stage and the decoded output are each limited to 65,536 bytes, so an encoded representation can reach its input limit before its decoded document reaches the output limit.

A `vault-json` payload contains exactly two fields, `encoding` and `payload`. The inner payload is another string and its encoding is one of the same four names. A JSON envelope can therefore contain another JSON envelope, up to eight envelope layers. Unknown fields, duplicate fields and additional layers are rejected. These layers are containers for text representation. They do not encrypt the text, conceal it from someone holding the payload or give access to a remote vault.

```python
import json
from madrigal_lab import recovery

envelope = json.dumps({'encoding': 'hex', 'payload': '63617265'})
decoded = recovery.decode(envelope, 'vault-json')
assert decoded['text'] == 'care'
assert decoded['layers'] == ['vault-json', 'hex']
assert decoded['cryptographic_decryption'] is False
```

The decoder returns the text, its byte count, its calculated SHA-256 digest and the encoding layers. It does not evaluate scripts, import code described by the payload or execute document contents. Binary documents that are not valid UTF-8 need another tool and are rejected here. The term “vaultception” describes this edition's nested encoding demonstration; it does not establish an external standard or an encrypted-vault compatibility claim.

## Compare a backup before restoring it

`recovery.inspect_backup(record)` requires `backup` and `owner_asserted: true`. `backup` is the supplied text, not an arbitrary path on disk, a URL or a remote account reference. `encoding` is optional and defaults to `utf8`. An optional `expected_sha256` must be exactly 64 lowercase hexadecimal characters. Without that digest the result says `integrity: 'not compared'`. With one it reports either `matches` or `mismatch`.

```python
import hashlib
from madrigal_lab import recovery

backup = 'My local notes\n'
expected = hashlib.sha256(backup.encode('utf-8')).hexdigest()
inspection = recovery.inspect_backup({
    'backup': backup,
    'owner_asserted': True,
    'expected_sha256': expected,
})
assert inspection['integrity'] == 'matches'
assert inspection['ownership_verified'] is False
assert inspection['authenticity_verified'] is False
```

Calculating the expected digest from the same text is useful for this example, but it gives no independent historical evidence. In a real backup review, compare against a digest you retained separately when the backup was made or received through a trusted process. A matching digest says the supplied bytes equal the bytes represented by that digest. It does not identify their author, verify testimony, prove ownership or grant account access.

## Create a new local document

`recovery.restore(runtime, record)` accepts the inspection fields plus `target`. Both `expected_sha256` and `target` are required for a restore. The expected digest must match before the module attempts a filesystem change. The destination is a new relative document path under the supplied `Runtime`'s `files` directory. Existing files and directories cannot be overwritten. Absolute paths, hidden paths, empty path segments, `.` or `..` segments, backslashes and symlinks are rejected.

```python
import hashlib
from madrigal_lab import recovery
from madrigal_lab.runtime import Runtime

runtime = Runtime('.lab-state')
backup = 'My local notes\n'
receipt = recovery.restore(runtime, {
    'backup': backup,
    'owner_asserted': True,
    'expected_sha256': hashlib.sha256(backup.encode('utf-8')).hexdigest(),
    'target': 'recovered/notes-copy.txt',
})
assert receipt['status'] == 'local-document-restored'
assert runtime.read('recovered/notes-copy.txt')['text'] == backup
assert receipt['account_restored'] is False
```

Run this example once or choose another new target path. The receipt records the local path, byte count and digest, and explicitly records zero remote actions. It does not change the publication, a provider account, a password or anyone's permission records. The caller's runtime controls which local state directory is used; the web workbench uses its existing local state directory rather than accepting a recovery state path from the request.

The restoration checks the document-tree entry limit of 256, including new parent directories, before creation. It opens each absolute root ancestor without following symlinks, then counts and creates through anchored directory descriptors. This also rejects a state-directory ancestor that was replaced with a symlink after the runtime was constructed. The final file is created exclusively with owner-only file permissions, so competing attempts cannot replace one another's completed document.

Restore calls in the same process share a lock, including calls through different runtime instances. A nonblocking POSIX directory lock also coordinates cooperating restore calls in other processes. A busy directory returns a failed restore rather than waiting indefinitely. The count check and creation occur inside those locks, so two cooperating restores cannot both consume the same last document-tree slot. These locks do not govern unrelated programs that directly modify the directory; run such writers separately, or use the workbench server's serialized actions.

A failed digest comparison creates neither a file nor parent directories. If file creation fails after new parents were created, restoration attempts to remove only this call's newly created, empty directories whose identities still match. Preexisting directories and directories populated or replaced by another writer are retained. No successful restore is reported for that failure. This implementation uses the Linux/POSIX directory and locking facilities provided by the cloud environment.

## Review, evidence and paperwork

A useful private recovery record identifies the provider, the dated notice, the official route reviewed and a nonsecret support reference. It records whether the outcome is still pending, whether a provider decision arrived and whether a separate local document was restored. Keep sensitive evidence with the provider or in your own protected storage. Do not place passwords, identity documents, private recovery links or personal support transcripts in this public edition.

For a closed account, the account outcome and the document outcome can diverge. A permitted export can be returned even when an account stays closed. A backup can restore a local note even when a provider declines reopening. An appeal can be accepted before the owner has retrieved any data. Keeping these entries separate helps the owner describe what actually changed.

Recursive review is a bounded return through those recorded facts. It cannot turn repeated appeals into a guaranteed right of access, and it cannot turn decoding an envelope into deciphering a password. A new review can update the checklist or add a new document copy when the owner supplies new information. The provider remains responsible for its account decision, and the owner remains responsible for choosing which of their own documents to retain.

## Verification

Run `python -m unittest discover -s tests -p test_recovery.py -v` from the repository root. The focused checks exercise all four checklist cases; strict owner assertions and unknown-field rejection; UTF-8, hex and base64 round trips; the eight-layer JSON limit; invalid, binary and oversized payloads; digest comparisons; new-only local restoration; path and symlink confinement; replaced root ancestors and a symlink-parent replacement race; competing targets across runtime instances; directory lock contention; the document entry limit; rollback of empty parents while preserving unrelated contents; and absence of network access or payload execution. They test this module's behavior and do not certify an external provider's recovery procedure.
