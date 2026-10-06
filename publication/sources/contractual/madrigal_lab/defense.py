"""Unchanged Guardian observations exposed to the local lab."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'vendor' / 'guardian'
spec = importlib.util.spec_from_file_location('mechanics', FOLDER / 'mechanics.py')
mechanics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mechanics)
sys.modules['mechanics'] = mechanics
spec = importlib.util.spec_from_file_location('lab_guardian', FOLDER / 'guardian.py')
guardian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardian)


def scan(root):
    report = guardian.inventory(root)
    report['complete'] = not report['errors']
    report['file_count'] = len(report['files'])
    report['exit_code'] = 2 if report['errors'] else int(bool(report['findings']))
    report['scope'] = 'Read-only file indicators; no process, network, archive or prevention engine'
    return report


def baseline(root, destination, trusted=False):
    if trusted is not True:
        raise ValueError('A baseline requires explicit known-good confirmation')
    root = Path(root).resolve(strict=True)
    dest = Path(destination).resolve()
    if dest.is_relative_to(root):
        raise ValueError('Baseline must be outside target')
    report = scan(root)
    if not report['complete'] or report['findings']:
        raise ValueError('Review findings and errors before establishing a trusted baseline')
    with dest.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
    return report


def check(root, baseline_path):
    old = json.loads(Path(baseline_path).read_text())
    report = scan(root)
    report['changes'] = guardian.compare(old, report)
    report['findings'].extend(mechanics.correlate(old, report, report['changes'], 10))
    report['summary'] = mechanics.summarize(report)
    report['changes_are_incomplete'] = not report['complete']
    report['exit_code'] = 2 if not report['complete'] else int(bool(report['findings'] or any(report['changes'].values())))
    return report


def inspect_bytes(label, data):
    """Apply unchanged Guardian primitive/composite rules to a bounded bot payload."""
    if not isinstance(data, bytes) or len(data) > 65536:
        raise ValueError('Bot inspection accepts at most 64 KiB')
    features = mechanics.primitives(label, data)
    suspicious = Path(label).suffix.lower() in guardian.EXTENSIONS or Path(label).name.lower() in guardian.NOTES
    findings = mechanics.composites(label, features, suspicious)
    if guardian.EICAR in data:
        findings.append({'path': label, 'kind': 'antivirus-test-file', 'detail': 'Harmless EICAR test marker'})
    if suspicious:
        findings.append({'path': label, 'kind': 'ransomware-name-indicator', 'detail': 'Filename indicator only; manual review required'})
    return {'primitives': features, 'findings': findings, 'scope': 'Bounded payload indicators, not a safety verdict'}
