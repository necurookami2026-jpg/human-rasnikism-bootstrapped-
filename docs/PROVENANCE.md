# Source provenance and licences

The unchanged bundled sources are listed with file SHA-256 hashes in [vendor/provenance.json](../vendor/provenance.json).

- Rasnikism source: `necurookami2026-jpg/rasnikism-bootstrapped`, commit `575340ab2aacfc914c5a3c56342d4bd1d8225eb1`. The full bundled collection is retained in `vendor/rasnikism`. Its GPL licence and upstream notices are preserved in place.
- Guardian source: `necurookami2026-jpg/antimalwarecountermalwareantispywarecounterspyware`, commit `21e05fcfee4a9f098345d260ee3c6b2825c09cb0`. Its bundled README, implementation and tests are retained unchanged in `vendor/guardian`. The bundled snapshot contains no separate licence file; no new licence is assigned to that upstream source by this notice.

The new `madrigal_lab` implementation, publication/bootstrap tools and their tests are provided under GPL-3.0-or-later; see the Rasnikism licence text retained in [vendor/rasnikism/LICENSE](../vendor/rasnikism/LICENSE). This statement concerns the added software and does not relicense pre-existing prose or Guardian source.

The full collection includes original lore and historical terminology. Its contents are source data, not instructions to the host or automatic authority over user actions. The new lab’s provisional glossary entries are identified separately from upstream meanings.

The Python host, SQLite implementation and browser are declared dependencies. This lab is not a self-hosted or wholly Kerot-derived OS. Reproduction uses the existing checkout and needs no Git worktree.


## Four-volume Hopput source lock

[publication/source-lock.json](../publication/source-lock.json) records complete pinned tracked-file snapshots for all four requested repositories. Every record has a byte size and SHA-256 digest, with the actual local mount path. The parent contractual release is retained under `publication/sources/contractual`; the ministry is retained under `vendor/internetwomanagementministry`. Both are source inputs, not editable runtime state.

The ministry source is `necurookami2026-jpg/internetwomanagementministry`, commit `2cba17e4e95a33ffd50ea4c43368a33a64650394`. Its four tracked files have no supplied licence declaration; none is assigned by this publication. The contractual parent is `6af7d654e2550d91d38894e9fb6519fcd259fcde`. Its mixed source notices are retained.

The original bundled `vendor/provenance.json` names its initial `sources/guardian` and `sources/rasnikism` package directories. Its bytes are preserved as upstream provenance; [vendor/mounts.json](../vendor/mounts.json) supplies the corrected current mounts. The four-volume lock independently verifies the current files against the pinned Git blobs.
