"""Observable primitives and explainable composites; none is a malware verdict."""
from collections import Counter
import math
from pathlib import Path

SAMPLE_LIMIT = 65536
SCRIPT_SUFFIXES = {'.py', '.ps1', '.js', '.vbs', '.sh', '.bat', '.cmd'}
DOCUMENT_SUFFIXES = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.png'}


def entropy(sample):
    if not sample:
        return 0.0
    return round(-sum((n / len(sample)) * math.log2(n / len(sample))
                      for n in Counter(sample).values()), 4)


def primitives(path, sample):
    """Only inspect a bounded prefix; return evidence labels, never file contents."""
    path = Path(path)
    value = entropy(sample)
    signals = []
    if len(sample) >= 4096 and value >= 7.5:
        signals.append('high-entropy-prefix')
    if sample.startswith(b'MZ') or sample.startswith(b'\x7fELF'):
        signals.append('executable-header')
        suffixes = [suffix.lower() for suffix in path.suffixes]
        if path.suffix.lower() in DOCUMENT_SUFFIXES or any(s in DOCUMENT_SUFFIXES for s in suffixes[:-1]):
            signals.append('document-name')
    if path.suffix.lower() in SCRIPT_SUFFIXES:
        text = sample.decode('utf-8', errors='replace').lower()
        if any(token in text for token in ('invoke-webrequest', 'downloadstring(', 'curl ', 'wget ')):
            signals.append('download-text')
        if any(token in text for token in ('invoke-expression', 'iex ', '| bash', '| sh')):
            signals.append('execution-text')
        if any(token in text for token in ('pynput.keyboard', 'keyboard.hook(', 'getasynckeystate')):
            signals.append('keyboard-capture-text')
        if any(token in text for token in ('requests.post(', 'socket.send(', 'sendall(', 'invoke-restmethod')):
            signals.append('network-send-text')
    return {'entropy': value, 'sample_bytes': len(sample), 'primitives': signals}


def finding(path, kind, severity, evidence, detail):
    return {'path': path, 'kind': kind, 'severity': severity,
            'evidence': evidence, 'detail': detail}


def composites(path, features, suspicious_name=False):
    signals = set(features['primitives'])
    if suspicious_name:
        signals.add('ransomware-name-indicator')
    rules = [
        ('executable-masquerading', 'high', {'executable-header', 'document-name'},
         'Executable header with a document-like name; review before opening'),
        ('download-and-execution-text', 'medium', {'download-text', 'execution-text'},
         'Script contains download and execution tokens; legitimate installers may also match'),
        ('keyboard-capture-and-send-text', 'high', {'keyboard-capture-text', 'network-send-text'},
         'Script contains keyboard capture and network send tokens; inspect intent manually'),
        ('possible-encrypted-ransomware-output', 'high', {'high-entropy-prefix', 'ransomware-name-indicator'},
         'High-entropy prefix with a ransomware-style filename; not proof of encryption'),
    ]
    return [finding(path, kind, severity, sorted(required), detail)
            for kind, severity, required, detail in rules if required <= signals]


def correlate(baseline, current, changes, threshold=10):
    """Correlate changes, suppressing global inferences on incomplete scans."""
    if baseline.get('errors') or current['errors']:
        return []
    alerts = []
    entropy_jumps = []
    for path in changes['modified']:
        old, new = baseline['files'][path], current['files'][path]
        if (old.get('sample_bytes', 0) >= 4096 and new.get('sample_bytes', 0) >= 4096
                and new.get('entropy', 0) >= 7.5
                and new['entropy'] - old.get('entropy', 8) >= 2.0):
            entropy_jumps.append(path)
            alerts.append(finding(path, 'possible-encryption-change', 'high',
                                  ['hash-changed', 'entropy-increased'],
                                  'File content changed from lower to high entropy; compression can also cause this'))
    changed = len(changes['modified']) + len(changes['removed'])
    total = len(baseline['files'])
    if changed >= threshold and total and changed / total >= 0.25:
        alerts.append(finding(None, 'widespread-file-change', 'medium',
                              [f'{changed} modified or removed files', f'{total} baseline files'],
                              'At least 25% of baseline files changed; bulk edits can also cause this'))
    if len(entropy_jumps) >= threshold:
        alerts.append(finding(None, 'widespread-possible-encryption', 'high',
                              [f'{len(entropy_jumps)} entropy increases'],
                              'Multiple modified files became high entropy; investigate immediately'))
    return alerts


def summarize(report):
    counts = {'info': 0, 'medium': 0, 'high': 0}
    for item in report['findings']:
        severity = item.setdefault('severity', {'antivirus-test-file': 'info',
                                               'known-hash': 'high'}.get(item['kind'], 'medium'))
        counts[severity] += 1
    return {'files_scanned': len(report['files']), 'errors': len(report['errors']),
            'findings_by_severity': counts,
            'review_priority': next((s for s in ('high', 'medium', 'info') if counts[s]), 'none'),
            'complete': not bool(report['errors']),
            'notice': 'Indicators require review; absence of findings does not establish safety'}
