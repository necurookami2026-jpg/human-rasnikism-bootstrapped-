# Combined Rasniki Hopput bootstrap

Run from the existing checkout; cloud tasks are already isolated and require no new Git worktree. Python 3.10+, Node.js and a POSIX shell are the declared hosts. No third-party packages, new credentials or network access are required to rebuild the included collection.

```sh
sh bootstrap.sh
```

The bootstrap verifies all 254 pinned source records before construction. It then runs the current lab/publication Python tests, the Guardian Python suite, the ministry’s Node smoke checks and desktop JavaScript syntax check. It separately exercises the pinned contractual parent’s test suite in a temporary source copy, then copies Rasnikism to another temporary writable directory and runs its complete upstream bootstrap, which rebuilds quilt/program artifacts and publications and executes the Python and JavaScript suites. The retained source roots remain unchanged.

The combined builder writes its reading files, catalogue, source archive and output hashes to `publication/edition/`. It rebuilds them in another temporary directory and checks byte equality. A final source verification detects changes to a pinned source. Failure of a required command produces a nonzero bootstrap exit status. Logs and a receipt are retained outside the source snapshots, under ignored `.publication-build/bootstrap/`.

The receipt records exact commands, exit codes, host versions, the source-lock digest and output digests. Its `checks_passed` field means these named checks passed for that run. It is neither a safety certificate nor proof of universal exact science. The receipt is a local execution record, not a signed or independently timestamped release.

## Verify and rebuild the publication alone

```sh
python3 tools/publication.py verify
python3 tools/publication.py build
python3 tools/publication.py build --check
```

Verification refuses missing, changed, unsafe or out-of-range source inputs. Building treats documents and programs as archived data; it does not execute their payloads. The offline HTML reader presents source text and a recursively nested lair index with parent-return navigation. Depth and node limits bound its traversal. The ZIP preserves source bytes and relative identities, including original licences and the original HTML mirrors. Public application hosting is not part of this command.

## Start the local environment

```sh
python3 -m madrigal_lab --port 8765
```

Use the desktop’s collection links for the Hopput publication, original Rasnikism studio and ministry archive. The server binds only loopback. The new HTML reader can also be opened directly from `publication/edition/index.html` without starting a server.

The service retains documents, practice records and demo accounting under ignored `.lab-state/`. Live processes and session tokens restart after restoration. The internet bot stays disabled until an operator enables an explicitly requested HTTPS host. Firmware, protected-kernel and real financial functions remain simulations or future milestones as documented in the implementation contract.
