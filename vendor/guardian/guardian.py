#!/usr/bin/env python3
"""Read-only local file scanner and integrity monitor (Python 3.10+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
from datetime import datetime, timezone

from mechanics import SAMPLE_LIMIT, primitives, composites, correlate, summarize

EICAR = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
EXTENSIONS = {'.locked', '.encrypted', '.crypt', '.lockbit', '.wncry'}
NOTES = {'readme_decrypt.txt', 'how_to_decrypt.txt', 'decrypt_instructions.txt'}


def inventory(root, signatures=None, excluded=()):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Target must be a directory')
    excluded = {Path(p).resolve() for p in excluded}
    files, findings, errors = {}, [], []
    def walk_error(error):
        errors.append({'path': str(error.filename), 'error': str(error)})
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        dirs[:] = sorted(d for d in dirs if d != '.git' and not Path(directory, d).is_symlink())
        for name in sorted(names):
            path = Path(directory, name)
            if path.is_symlink() or path.resolve() in excluded:
                continue
            relative = path.relative_to(root).as_posix()
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(fd, 'rb') as stream:
                    before = os.fstat(stream.fileno())
                    if not stat.S_ISREG(before.st_mode):
                        continue
                    digest, tail, marker, sample = hashlib.sha256(), b'', False, b''
                    while chunk := stream.read(1024 * 1024):
                        digest.update(chunk)
                        if len(sample) < SAMPLE_LIMIT:
                            sample += chunk[:SAMPLE_LIMIT - len(sample)]
                        window = tail + chunk
                        marker = marker or EICAR in window
                        tail = window[-len(EICAR):]
                    after = os.fstat(stream.fileno())
                    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                        raise ValueError('File changed during scan; retry')
                sha = digest.hexdigest()
                features = primitives(relative, sample)
                files[relative] = {'sha256': sha, 'size': after.st_size, **features}
                if marker:
                    findings.append({'path': relative, 'kind': 'antivirus-test-file', 'detail': 'Harmless EICAR test marker'})
                if signatures and sha in signatures:
                    findings.append({'path': relative, 'kind': 'known-hash', 'detail': signatures[sha]})
                suspicious_name = path.suffix.lower() in EXTENSIONS or name.lower() in NOTES
                if suspicious_name:
                    findings.append({'path': relative, 'kind': 'ransomware-name-indicator', 'detail': 'Filename indicator only; manual review required'})
                findings.extend(composites(relative, features, suspicious_name))
            except (OSError, ValueError) as error:
                errors.append({'path': relative, 'error': str(error)})
    report = {'version': 2, 'root': str(root), 'files': files, 'findings': findings,
              'errors': errors, 'scanned_at': datetime.now(timezone.utc).isoformat()}
    report['summary'] = summarize(report)
    return report


def compare(baseline, current):
    if baseline.get('version') not in (1, 2) or baseline.get('root') != current['root']:
        raise ValueError('Baseline version or root does not match')
    old, new = baseline['files'], current['files']
    if not isinstance(old, dict) or any(not isinstance(v, dict) or not isinstance(v.get('sha256'), str)
                                       or not isinstance(v.get('size'), int) for v in old.values()):
        raise ValueError('Invalid baseline file records')
    return {'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()),
            'modified': sorted(p for p in old.keys() & new.keys()
                               if (old[p]['sha256'], old[p]['size']) != (new[p]['sha256'], new[p]['size']))}


def load_signatures(path):
    if not path:
        return {}
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or any(not isinstance(k, str) or len(k) != 64 or any(c not in '0123456789abcdef' for c in k) or not isinstance(v, str) for k, v in data.items()):
        raise ValueError('Signatures must map lowercase SHA-256 hashes to string labels')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['scan', 'baseline', 'check', 'watch'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--signatures', type=Path)
    parser.add_argument('--interval', type=float, default=10)
    parser.add_argument('--change-threshold', type=int, default=10,
                        help='Minimum changed files for aggregate alerts (default: 10)')
    args = parser.parse_args(argv)
    if args.command != 'scan' and args.baseline is None:
        parser.error('--baseline is required')
    if not 0 < args.interval < float('inf'):
        parser.error('--interval must be positive and finite')
    if args.change_threshold < 1:
        parser.error('--change-threshold must be at least 1')
    try:
        signatures = load_signatures(args.signatures)
        excluded = [p for p in (args.baseline, args.signatures) if p is not None]
        baseline = json.loads(args.baseline.read_text()) if args.command in ('check', 'watch') else None
        previous = None
        while True:
            report = inventory(args.directory, signatures, excluded)
            if args.command == 'baseline':
                if report['errors']:
                    raise ValueError('Cannot save incomplete baseline: ' + json.dumps(report['errors']))
                with args.baseline.open('x') as stream:
                    json.dump(report, stream, indent=2)
                    stream.write('\n')
            if baseline is not None:
                report['changes'] = compare(baseline, report)
                report['findings'].extend(correlate(baseline, report, report['changes'], args.change_threshold))
                if report['errors']:
                    report['changes_are_incomplete'] = True
                if previous is not None:
                    report['interval_changes'] = compare(previous, report)
                    report['interval_findings'] = correlate(previous, report, report['interval_changes'], args.change_threshold)
                    if previous['errors'] or report['errors']:
                        report['interval_changes_are_incomplete'] = True
            report['summary'] = summarize(report)
            print(json.dumps(report, indent=2), flush=True)
            if args.command != 'watch':
                return 2 if report['errors'] else int(bool(report['findings'] or any(report.get('changes', {}).values())))
            previous = report
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
