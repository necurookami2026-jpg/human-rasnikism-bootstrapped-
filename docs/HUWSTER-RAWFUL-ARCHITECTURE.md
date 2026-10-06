# Huwster Rasnikism — Ostar Rawful architecture and runtime

## Default architecture and design sequence

Publication edition 11 renovates the working title to Huwster Rasnikism and makes Ostar Rawful the default workbench and drafting mode. “Rawful” means the supplied inputs, construction method, literal output and limits remain visible. It is not a synonym for lawful, legal approval or a waiver of applicable requirements. The historical Max Law and Max Lawful reading guides remain preserved as earlier editorial perspectives. “Oscar lawful” is not the selected default or a new legal classification.

The default workspace opens the regenerative architecture and life-simulation IDE. Its engineering sequence begins with systematic ecorestoration or regenerative design, then considers incremental environmentalism or green consumerism inside the declared system boundary. Regenerative design addresses relationships among land, water, habitat, infrastructure, resources and community participation. Incremental choices address particular consumption or operating decisions. The software records both scales instead of claiming that a consumer choice by itself restores an ecosystem.

The world engine requires a `restore` record for a place before accepting its `consume` operation. This enforces the declared planning sequence, not proof that restoration has occurred. Habitat, water and consumption are bounded toy scores with deliberately simple rules. An actual project requires a baseline, field observations, calibration, impact assessment, engineering review and qualified jurisdiction-specific legal review. Society and societal relationships are represented by voluntarily supplied fictional actors, places, roles, dependencies and signals; the engine does not model actual populations without data or predict social outcomes.

## Complete 7^8 legal-drafting corpus

The user selected generation of every individual document rather than an on-demand-only catalogue. `publication/rawful-corpus/` contains **5,764,801 individual Markdown drafts**, packaged as 49 reproducible `.tar.gz` archives. Each archive contains 117,649 separate files named `documents/0000001.md` through `documents/5764801.md` across contiguous ranges. Extraction produces the individual numbered files. The archives total far less space than the extracted corpus; allow substantial disk space before extracting the entire collection. The manifest records exact counts, ranges, sizes and SHA-256 hashes.

The eight base-seven coordinates are: three subject-slot digits, one context digit, one document-purpose digit, one review-facet digit, and two revision digits. That is `343 subject slots × 7 contexts × 7 purposes × 7 facets × 49 revisions = 7^8`. The user-supplied encounter categories occupy the first named slots. Remaining slots are explicitly unassigned, allowing the entire numeric space to be generated without inventing parties or facts. Numeric addresses in paperwork are one-based digits 1–7; the implementation internally uses zero-based coordinates 0–6. Document indexes are one-based.

Seven contexts are architecture, interactive, roleplay, jobrole, runtime, ecorestoration and franchise. Seven purposes are scope/parties, permissions/consent, resources/impact, design/obligations, evidence/review, change/remedy and closure/reuse. Seven facets are identity, authority, ownership, participation, environment, operation and revision. Their Cartesian product yields **49 distinct purpose/facet documents per category, context and revision**. Each draft has its own index, address, category, context, revision, purpose and facet, explanatory prose and explicit unresolved review fields. The documents are templates within a finite schema, not millions of bespoke legal opinions.

Each draft records that jurisdiction, party identity, authority, rights, consent, measurements, qualified review, signature and legal effectiveness have not been established. The user can personalise a 49-document packet in the workbench, but the presence of a file does not bind an encountered subject or grant ownership, franchise rights, employment or consent. Creating drafting paperwork is implemented; legal effectiveness is a matter for the relevant facts and legal process.

Build or resume the full corpus with:

```sh
python3 tools/build_rawful_corpus.py --workers 4
python3 tools/verify_rawful_corpus.py
```

The generator has no network operation. It writes each individual file into an archive as a stream, so it need not store millions of loose files during generation. Fixed archive metadata makes regeneration reproducible. Verified completed shards can be reused; the default generator completes all 49. The full-corpus verifier checks archive hashes, contiguous ranges, exact count and the current document-generation inputs. The manifest is separately included with publication outputs. Bootstrap verifies the corpus; it does not silently generate another five million documents each run.

## Encounter categories and default paperwork

The full category inventory is machine-readable in `HUWSTER-ARCHITECTURE.json` and the workbench selector. It retains these requested labels: bot, robot, droid, device, pager, mobile, portable, tablet, laptop, desktop, mainframe, hive, colony, suite, room, floor, layer, tier, condominium, condo, name, stamp, bednob, seal, home, house, empire, special-economic, hamlet, field, ville, bathway, driveway, byway, roadway, streetway, carriageaway, motorway, interstateway, town, shop, store, mall, person, citizen, people, demographic, individual, group, collective, pal, family, fam, tribe, pace, species, creture, nonindividual, nongroup and noncollective.

The supplied “special economic” is represented by the script-safe label special-economic. The repeated ville has one category address, while supplied alternative spellings such as family/fam and condominium/condo retain separate addresses. Category labels identify a drafting subject type, not a verified person, species, device or political jurisdiction. Names, stamps and seals do not authenticate authority.

Each actor and place encountered by the simulation automatically receives references to all 49 documents in each of the interactive, roleplay and jobrole contexts: 147 default references per encountered record. Habitat maps to field, home to home, work to room, road to roadway and shop to shop. The references point to the fully generated corpus; encounter processing does not create duplicate millions-file corpora. A user-selected packet provides personalised prose for the supplied subject. The application does not discover real devices or people, crawl accounts, read contacts, classify demographics or impose paperwork on external clients.

## Full career, roleplay and jobrole ranks

`HUWSTER-RANKS.json` contains all **3,087 rank records**: three kinds, seven types per kind, three contexts and 49 ranks per type/context. Each rank is a distinct seven-stage by seven-facet address. Ranks organise fictional work and practice; they do not create professional credentials or assign real employment.

Primitive types are mark, read, write, choose, step, signal and reference. The first six retain the historical K0 primitive names; reference is an authored modelling abstraction, not an added K0 opcode. Composite types are parcel, household, workgroup, habitat, infrastructure, community and series. Mechanic types are care, restraint, repair, truthfulness, stewardship, learning and advocacy. For every type, career, roleplay and jobrole each contain the full ranks 1–49. Earlier Ashram separation and grammar remain their own symbolic module rather than being silently expanded into K0 operations.

## IDE, assembler, compiler and runtime

Start the existing local service:

```sh
python3 -m madrigal_lab --port 8765
```

Open `http://127.0.0.1:8765/`. Architecture & life simulation is the initial workspace. The existing Language & boot workspace still provides K0 source formatting, assembly, disassembly, compilation, execution, simulated drivers and instruction budgets. Huwster adds a separate declarative world language compiled into structured JSON instruction records. It never passes supplied source to host `eval`, a shell or a native device driver.

World instructions are:

| Instruction | Arguments | Implemented behaviour |
| --- | --- | --- |
| world | quoted title | Declare exactly one world, first |
| place | name x y habitat/home/work/road/shop | Add a named place and default document references |
| actor | name x y category | Add a fictional actor and default document references |
| drive | actor x y | Set a simulated movement target |
| signal | actor-or-place quoted text | Record a message at the current tick |
| restore | place integer 0–100 | Increase bounded toy habitat/water indicators |
| consume | place integer 0–100 | Reduce toy consumption after a restore record |
| tick | integer 1–100 | Advance actors one grid step per axis toward targets |
| episode | quoted title | Record a numbered lore episode |
| franchise | quoted title | Record a proposed series line without granting rights |
| refranchise | quoted title | Record a proposed revision linked to the previous line |

The grid is 24 by 24; coordinates are 0–23. A run accepts at most 512 instructions, 64 places, 32 actors and 256 ticks plus its initial frame. Source accepts at most 16,000 UTF-8 bytes; arguments are bounded to 160 characters. Duplicate names, missing references, invalid categories, out-of-range values and unknown instructions produce inability errors. The user corrects the supplied input; no bound is bypassed. World names, role names and signals are displayed as inert text.

Compile creates the structured bytecode. Run interprets it into frames, signals, ecological indicators, encounter paperwork references, episode lore and franchise proposals. Play/pause and single-step replay show the run on a browser canvas. Source edits invalidate the previous result, preventing stale exports. The engine completes its finite run and hashes a canonical final-quilt JSON record. “Exact final catched finalised final quilt” names that reproducible bounded snapshot, not universal completion.

## Playable immersion and series exports

Download final quilt saves the full runtime evidence, input digest and snapshot digest. Download playable game saves a standalone HTML game with local frame playback, a frame selector and arrow-key movement of the first simulated actor. The portable game executes only the reviewed renderer; embedded user data is encoded so markup cannot inject scripts. It provides simple life-simulation immersion and editable fictional series structure, not the commercial Sims game, its assets or a production-scale 3D engine.

Episode records supply numbered series lore. Franchise and refranchise records are documented proposals; obtain rights evidence and qualified review before real licensing. Existing owned-media planning and animatic exports remain available in Media & series. No new claim of movie-quality rendering or externally hosted game publication follows from these local exports.

## Acceptance and relevant paperwork

The relevant records are this engineering contract, complete corpus manifest and archive hashes, every generated numbered draft, all career/roleplay/jobrole ranks, supplied world source, compiled instructions, literal run frames and signals, final-quilt digest, episode/franchise proposals, original source provenance and bootstrap receipt. Real measurements, permissions, licences and reviewer decisions remain separate evidence requirements.

Validation exercises numeric addressing, all requested category/context packets, all rank grids, movement, ecological update rules, planning order, signals, lore, default document references, bound failures, server action routes and portable-game rendering. The full existing bootstrap runs alongside corpus-integrity checks and repeated publication comparison. Publication retains the complete earlier corpus and licences while exposing Huwster Rasnikism and Ostar Rawful as the current title and default.
