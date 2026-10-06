# Validation record — 6 October 2026

The following checks executed in the cloud machine for this release:

| Check | Observed result |
| --- | --- |
| New lab suite | 19 tests passed, including HTTP workflows, path rejection, symlink-root rejection, persistence and concurrent double-spend rejection. |
| Quilt payload coverage | All 30 Boolean payloads across eight modes executed; all four exact-addition pairs returned the expected sums. |
| Rasnikism full bootstrap, in a writable source copy | 16 Python tests and 12 JavaScript suite files passed; publications rebuilt and the example emitted `REFRAME DECISION RECORDED`. |
| Guardian upstream suite | 14 tests passed. The error printed by its incomplete-baseline fixture was an expected tested condition. |
| Vendored source integrity | All 111 listed source files matched the supplied provenance SHA-256 hashes. |
| Browser workflow | Compilation/run, boot simulation, storage/scanning, demo economy, intranet bot, game, glossary, curriculum, mobile width and upstream history studio passed with no page errors. |
| Live HTTPS bot | An explicitly enabled read-only request to `example.org` returned HTTP 200 and 577 bytes with TLS verification enabled. The desktop’s internet bot remains disabled by default. |
| Saved startup instructions | Health and a compiled K0 `ready` program passed on the running local service. |
| Recursive project scan | Complete scan of 153 files, zero errors, five review indicators. See explanation below. |

The project scan used Guardian unchanged and returned review status 1, rather than a clean verdict. Four findings are detection-token strings in Guardian’s mechanics and synthetic detection fixtures in its test suite. One informational finding is the harmless EICAR marker in Guardian’s generated Python bytecode. These locations were reviewed against their source and the recorded upstream hashes. The report stays outside the scanned root at `/tmp/rasniki-project-scan.json`; no files were deleted, quarantined or altered in response to findings. Counts describe that run, including local generated/state files, rather than a permanent repository file count.

The first browser harness attempted an eval-based wait blocked by the desktop’s Content Security Policy. The harness was corrected to use DOM locator assertions; the application policy was retained. The final browser workflow passed after the bot-inspection changes and a service restart.

These checks validate the finite hosted implementation. Native boot, UEFI firmware execution, hardware virtualisation, a protected OS kernel, public DNS/hosting, real finance and universal scientific correctness were not tested or implemented.
