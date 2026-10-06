# Guardian: file scanning and integrity monitoring

A working starting point for the antiencryptcounterencryptantimalwarecountermalwareantispywarecounterspywareantipenfinalcounterpenfinalcounterhalleluhjah project.

Guardian is a read-only defensive tool for Linux, built with Python 3.10+ and no external dependencies. It combines primitive observations into explainable composite alerts for malware indicators, suspicious scripts, and possible encryption changes. It does not execute scanned files or modify them.

## Primitive and composite mechanics

| Primitive observations | Composite alert |
| --- | --- |
| Trusted SHA-256 match | Known-hash finding, labeled by your local database |
| Harmless EICAR marker | Antivirus test fixture, informational priority |
| Executable header + document-like name | Possible executable masquerading |
| Script download tokens + execution tokens | Possible download-and-execution script |
| Script keyboard-capture tokens + network-send tokens | Possible spyware-style script |
| High-entropy prefix + ransomware-style filename | Possible encrypted ransomware output |
| Modified hash + entropy increase of at least 2 bits/byte to at least 7.5 | Possible encryption change |
| At least 10 modifications/removals affecting at least 25% of baseline files | Widespread file changes |
| At least 10 modified files with qualifying entropy increases | Widespread possible encryption |

Findings include severity, descriptions, and evidence labels for composites. Reports include UTC timestamps, completeness, per-file primitives, and a review-priority summary. Priority is a rule label, not a probability or malware verdict. High entropy alone is not an alert: compressed files often have high entropy.

Full files are hashed and searched for EICAR using bounded-memory streaming. Other content heuristics inspect only the first 64 KiB; entropy is computed on that prefix, requires at least 4 KiB for alerts, and is measured in bits per byte. Script rules inspect UTF-8 text with replacement for invalid bytes and can match comments or benign source code. They are review aids, not execution analysis. There is no automatic signature download.

## Run

```bash
python3 guardian.py scan /path/to/files
python3 guardian.py baseline /path/to/files --baseline /path/outside/files/baseline.json
python3 guardian.py check /path/to/files --baseline /path/outside/files/baseline.json
python3 guardian.py watch /path/to/files --baseline /path/outside/files/baseline.json --interval 10
python3 guardian.py check /path/to/files --baseline /path/outside/files/baseline.json --change-threshold 20
python3 -m unittest -v
```

Create the baseline from files you already trust and protect it against modification. Existing baselines are never overwritten. Watch emits JSON reports against the original baseline until Ctrl+C. Store baselines and redirected reports outside the scanned directory.

Watch also includes `interval_changes` and `interval_findings` comparing consecutive scans after the first iteration. Baseline changes accumulate; they do not measure an attack rate. Interval comparisons describe changes observed between two scans, not exact change times. Aggregate correlations are suppressed when either scan is incomplete. Watch uses polling and can miss changes reverted between scans.

New baselines use format version 2 with entropy features. Version 1 baselines remain supported for hash comparison, but cannot establish entropy increases until you create a new baseline under a different filename. `--change-threshold` must be a positive integer and changes the minimum file count for aggregate alerts; it does not disable individual findings.

Optional `--signatures trusted-signatures.json` accepts a JSON object mapping lowercase SHA-256 hashes to string labels. Use a trusted source; nothing is downloaded automatically. Signature and baseline files are excluded when explicitly supplied. Symlinks, special files, and `.git` directories are skipped.

Exit codes for scan/check: `0` means no findings or changes among scanned files, `1` means findings or changes need review, and `2` means error or incomplete scan. Baseline also returns `1` when findings exist, although it saves the baseline; inspect it before trusting it. Watch reports errors per iteration; its final exit code does not summarize historical alerts. Files changing during a scan are reported as errors. Apparent removals in incomplete reports require review.

## Limits

This is not a full antivirus engine or system spyware detector. It does not inspect processes, browser activity, network traffic, archive contents, or decrypt encrypted content. Filename and script indicators can be false positives. Hash matching detects only supplied signatures; no findings does not establish safety. Monitoring observes changes after they happen and cannot prevent encryption, recover keys, or decrypt ransomware files. Concurrent directory changes are not an atomic snapshot; use a filesystem snapshot for stronger consistency when needed.

Keep separate, tested offline backups for recovery. If compromise is suspected, isolate affected devices and use a trusted incident-response workflow. Guardian never deletes, quarantines, decrypts, or executes scanned files.

## Development

Use the existing checkout; no worktree is needed. Run `python3 -m unittest -v` before committing. No service startup, credentials, package installation, or network access is required.
