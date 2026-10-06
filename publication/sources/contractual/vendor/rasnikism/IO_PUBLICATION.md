# Encoded Ostar I/O publication

The document publication editions use .io scripts, with a browser reader at publication.html. Markdown remains an editorial source format, not the reader's required publication format. Encoded editions include the collection's documents, HTML interfaces, JavaScript, CSS, Python tools, tests, examples, manifests, and license. The executable kerot edition is published separately as actual source and bytecode under language/. Generated Markdown compilations are retained as earlier artifacts but are excluded from the bundles.

## Script format

The first line is `OSTAR_IO 1`. An `EDITION` instruction carries JSON metadata. Each `PUT` instruction carries a JSON record with a relative path, UTF-8 byte count, SHA-256 digest, and Base64 data. `END` closes the script. These are declarative I/O instructions, not shell commands, JavaScript evaluation, or automatic file writes.

Base64 is encoding, not encryption. SHA-256 checks accidental modification against the included digest; it does not authenticate the publisher or make an attacker-supplied bundle trustworthy. Payloads are never executed by the reader. Source text, including original document formatting, is preserved byte-for-byte.

## Use

Open publication.html to select an edition, search its records, read decoded text, and download a whole .io script or an individual decoded record. You can also import a .io script. The reader verifies every record before replacing its current collection. Unsupported instructions, invalid paths, duplicate paths, malformed Base64 or UTF-8, inconsistent sizes, and mismatched digests are rejected.

Reading imported content does not install software or approve its claims. Downloaded scripts and programs require the documented host to run; no operating system, legal service, or external action starts automatically. The three edition lenses preserve their existing limits, including the jurisdiction edition's unreviewed status.

## Build and limits

Run `python3 software/build_io_publication.py` from the repository root. It builds three .io files under encoded/ and the offline browser data script publication-data.js. It excludes .git, generated compilations, encoded outputs, Python caches, and its own generated data script. It preserves the actual license and canonical source bytes.

Import limits are 10 MiB of script text, 500 records, 2 MiB per decoded record, and 5 MiB total decoded bytes. Browser digest verification needs Web Crypto support. If unavailable, the reader reports failure rather than bypassing verification. This bundle is not self-booting or a kerot-only implementation.
