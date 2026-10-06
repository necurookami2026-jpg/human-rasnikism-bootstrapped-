# Rasniki Madrigal lab — implementation contract

Version 0.1.0, 6 October 2026. This is a runnable Python-hosted virtual lab with a browser desktop and the full bundled Rasnikism collection. It implements finite tools and records explicit simulation boundaries. The user’s “Madrigal” spelling is retained for the lab; upstream calls its proposed operating system “Magrigal.”

## Run and validate

Use the existing checkout; cloud tasks are already isolated and do not require another worktree. Python 3.10 or newer runs the lab. Node.js runs the bundled JavaScript tests. There are no third-party runtime packages to install.

From the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m madrigal_lab --port 8765
```

The desktop is available locally on port 8765. The development server binds only IPv4 loopback. It stores documents and records in ignored `.lab-state/`; use `--state /path/to/a/private/lab-directory` to choose another location. Stop with Ctrl+C. Files and SQLite records persist; the HTTP process, session token and transient boot traces do not survive a restart.

For a local readiness check:

```sh
curl --fail --silent http://127.0.0.1:8765/api/health
```

The response must contain `"status": "ok"`. A functional readiness check must also compile and run a program or use the existing HTTP workflow tests; health alone does not validate the language or storage.

Run the bundled upstream suites without rebuilding publications:

```sh
python3 -m unittest discover -s vendor/rasnikism/software -v
(cd vendor/guardian && python3 -m unittest -v)
for suite in vendor/rasnikism/software/test_*.cjs; do node "$suite"; done
```

`vendor/rasnikism/bootstrap.sh` is the full upstream rebuild. To preserve the imported snapshot’s hashes, run it in a separate writable copy of the source rather than update vendored artifacts silently.

## Language, interpreter and construction

K0 is the source-backed 65,536-byte virtual machine with sixteen registers and the six primitive instructions `mark`, `read`, `write`, `choose`, `step` and `signal`. It is emulated by the retained Python interpreter. It has no host filesystem, network or host-language evaluation instruction.

`madrigal_lab.language.assemble` constructs bytecode. `disassemble` reconstructs numeric primitive source, rejecting malformed instruction fields. `format_source` resolves labels and produces canonical assembly; it drops source comments. Assemble/disassemble/assemble must preserve bytes. A source/history studio retaining revisions is also available in the full upstream collection at `jerry-pop.html`.

The small Ras script compiler accepts `emit "text"`, `exact BIT BIT`, and `halt`, where each BIT is 0 or 1. It lowers those statements to primitive K0 assembly. It supports UTF-8 output and emits a stop signal automatically if needed. It is a deliberately small compiler, not a general Python or native machine-code compiler. Recompilation means running this same source-to-primitive pipeline again. No self-hosting compiler is claimed.

```text
emit "care: "
exact 1 1
halt
```

The result is `care: 2`. Each run reports `halted`, `waiting`, `fault` or `budget-exhausted`, plus output and instruction count. The default budget is 10,000 and the maximum is 100,000. Fresh memory is allocated for each run. A result never silently substitutes one state for another.

The quilt implements eight finite modes, preserved with upstream spellings. `counterantonymmakkakah` is explicitly mapped to upstream `counterantonymmakkkah`; `makkah` is a provisional alias of `makkakah`. The mode manifest names each Boolean field. All 30 Boolean payload combinations are executable. “Exact science” here means exact addition of two Boolean bits and the documented finite checks. It does not mean universal scientific proof, authenticated consent or legal approval.

The science hierarchy remains a compact symbolic tree. Its sixteen levels have fifteen four-way transitions: 4^15 = 1,073,741,824 potential terminal positions per formal stanza. `hierarchy.sample` returns at most 256 addresses. Sampled addresses are indexes, not generated prose records or executed ops.

## Boot, kernel, virtualisation and environment

A boot simulation validates K0 bytecode, records its digest, allocates fresh memory and runs the interpreter. The MBR simulation constructs only an in-memory 512-byte record ending in 55 AA. It is not a bootable disk image, contains no x86 boot adapter, and is never written to a device. UEFI mode records a simulated handoff trace; it creates no PE/COFF EFI executable and calls no firmware services. Pseudo-ROM means a host-held copy of bytecode.

The kernel model maintains a bounded cooperative job queue. Emergency jobs precede urgency jobs; equal priorities preserve queue order. A tick runs one ready job under a finite budget and records its terminal status. A waiting or exhausted job is retained as such; this queue does not resume live K0 memory. The upstream interpreter/studio separately supports explicit input pause/resume. Neither the queue nor K0 supplies hardware privilege separation or a production hypervisor.

The native environment is the Python host plus the browser desktop. Native boot, device drivers for real hardware, a protected kernel, a hardware virtualisation backend and a standalone OS remain future milestones. Simulated device ports in the upstream studio have declared finite behavior.

## Storage, browser, bots and servers

The explorer writes and reads UTF-8 documents under its own root. Absolute paths, parent traversal, hidden paths and symlinks are rejected. Documents are limited to 64 KiB; the local lab has a document-count limit. The reader displays text rather than execute it. The bundled collection adds its existing reading editions, search, programs, encoded publications, glossary and studio.

The `.lab` domain host is a persistent local registry mapping names to existing documents. It performs no DNS registration, changes no system resolver and registers no public domain. The intranet bot reads only those records. The internet bot is disabled until the operator starts the server with an explicit destination, for example `--allow-host example.org`. It accepts HTTPS port 443, preserves default TLS/proxy trust, rejects credentials, literal IP addresses, local names and redirects, times out after five seconds, and bounds responses to 64 KiB. Returned content remains text and carries a bounded Guardian primitive/composite observation report. The intranet bot carries the same per-document observations. There is no autonomous crawling, posting, login or script execution.

The HTTP desktop/API is a local development internet-protocol server. Mutation requests require a per-session token and same-origin checks. Host-header validation rejects DNS rebinding names. No CORS allowance is provided. The game server shares a tiny target game through this local API; it is not a deployed multiplayer platform. Public hosting, authenticated remote accounts, certificates, public DNS and internet access policy must be separately configured for any future deployment.

## Defensive observations

The defensive adapter uses the unchanged Guardian `inventory`, comparison and mechanics functions. It scans only the lab’s document root. Symlinks, `.git` and special files are skipped. Full-file hashing and harmless EICAR detection stream in bounded memory; other content heuristics inspect the first 64 KiB. Filename, download/execute, spyware-style and possible encryption indicators require review and can match benign source or comments.

Reports distinguish completeness, file count, findings, errors and exit status. A trusted baseline must be explicitly confirmed as known-good, stored outside the scanned root, and newly created without overwriting an existing baseline. This wrapper additionally refuses to establish a baseline with unresolved findings. Comparisons report additions, modifications and removals; incomplete results remain marked incomplete.

The requested antimalware, countermalware, counterspyware and counterransomware labels refer to this shared read-only observation layer. They do not represent separate antivirus engines. Process inspection, traffic inspection, archive extraction, active prevention, quarantine, decryption, automatic recovery and continuously retained monitoring are not implemented. No scan result establishes that a system is safe.

## Demo accounts and economic management

The account manager stores named DEMO_CREDIT accounts in SQLite. The simulated mint issues units against an equal negative issuer position. Transfers post equal negative and positive amounts in a single transaction, reject insufficient balances and preserve circulation. Amounts are bounded positive integers; floats and booleans are rejected. Transactions are retained and reports verify balance by entry and in aggregate.

The financial manager exposes these postings and account totals. The economic manager reports demo issuance and circulation. “Economic minister” is a proposed steward role for reviewing those records, not a public office. There are no passwords, real bank accounts, sovereign currency, securities, credit promises, external payments, tax decisions or regulatory authorisations. This is a demonstration ledger rather than a private state mint.

## Practices, terminology, curriculum and franchise

The [recursive workbench](RECURSIVE-WORKBENCH.md) extends the local desktop with a [630-label atlas](RECURSIVE-SYSTEMS-ATLAS.md), ten prose formats, deterministic original fandom prompts, manual coordinate SVGs and persisted local boards. The atlas supplies bounded per-label advice/guidance and pagination; it declares omitted branches. BoardStore requires an explicit consent assertion for every mutation, limits records to 256, parent depth to eight, and combined interactions to 1,024. Surveys count submitted choices rather than authenticated people. Only reviewed quests contribute fictional points. Typed media, logistics, health, radio and community records do not confer their named real-world services.

The [demo economy extension](DEMO-ECONOMY-CONTRACTS.md) transfers existing DEMO_CREDIT balances into funded obligations and repays them atomically, retaining bounded portfolios and documentary contract versions. Coupons annotate a budget without moving units. Contract hashes compare local content and receipts; they authenticate no identity or legal authority. The [owner recovery module](OWNER-RECOVERY.md) supplies official account recovery plans, bounded data encoding and exclusive new-file restoration from owned backups with an expected digest. It performs no password guessing or remote access bypass.

The [owned-media studio](MEDIA-DATA-RENDITION.md) provides browser-local playback, raster brightness/contrast/crop edits, finite owned-data fingerprints and original seed renditions. Book text becomes a bounded episode/scene/shot plan. Canvas text cards can preview that plan or record a WebM draft. Local media is not uploaded. Permission withdrawal clears previews and prevents exports from a pending withdrawn recording. The output is an animatic rather than a guaranteed cinema-quality production; [device and safeguarding boundaries](SAFEGUARDING-AND-DEVICE-SCOPE.md) remain explicit.

The symbolic-practice tab uses `madrigal_lab.symbolic.catalogue`, `evaluate` and `compare`. Five fictional archetypes support voluntary reflection; the user spelling `thaumturgy` is an explicit alias of `thaumaturgy`. Six nonempty support texts each earn one Easterbunny documentation-presence point. Comparisons clear implementation/evidence fields for the documentation-only baseline, and all support fields for the absent-input baseline. References remain inert and unverified. The API requires explicit Boolean consent and opt-out values, bounds UTF-8 bytes, rejects unknown fields and performs no filesystem or network I/O. Browser evaluation stores no record on the server; an accepted result can be deliberately downloaded as JSON. Changing or clearing the form invalidates export and prevents a pending response from redisplaying its previous reflection.

The [spiritual workbench volume](SPIRITUAL-SYMBOLIC-WORKBENCH.md) explains the rubric and spiritual/fictional scope. The [conflict-protection library](CONFLICT-PROTECTION-LIBRARY.md) adds ten distinct templates for accessible voluntary participation, observation, dialogue, civilian support and correction. These are editorial workflows with bounded review, not combat automation, authority over opponents or guarantees of permanent protection.

Practice records follow proposed, active, paused, releasing and closed states with explicit permitted transitions and retained reasons. A closed record is not silently reopened. Emergency and urgency are prioritisation labels; they dispatch no emergency service. Nomic revision means a proposed rule can be recorded, reviewed and adopted, with a parent record for later revisions. Reviewer names are supplied assertions; no authenticated election or legal adoption is claimed.

The dictionary separates source-defined meanings, finite executable modes, proposed conventions, provisional spelling aliases and entries awaiting author definitions. The user’s counterabolshivik, counteraantonymbloshivik, bloshivik, aaantonymbolshivik, henapenall, counteraemergency and counterurgency terms remain explicitly unresolved. They refer to no identified political group and trigger no action against people. A new definition requires a recorded revision and tests if it acquires executable semantics.

Prototypes refer to this host implementation and its examples. Archetypes are maintainer, reviewer, learner and steward. Paradigms are bounded execution, explicit evidence, versioned repair and double-entry accounting. Twelve curriculum exercises cover construction, storage, practice handoff, accounting, integrity review, symbolic support comparison, conflict review, local boards, obligations, owned backup restoration, workpapers/maps and owned media. The ashram model is voluntary practice and learning. Sovereignty remains fictional governance vocabulary. The SVG shield is decorative heraldry and grants no title or authority.

The derivative/franchise manifest records components, source provenance, version and declared limits. It is a reproducible description, not a licence to use marks, operate businesses or bind beneficiaries. Formation identifies an implementation; reformation changes a reviewed version; format and reformat concern representation; franchise and refranchise concern proposed separately authorised derivatives. The prose charter’s unresolved legal particulars remain unresolved by this software.
