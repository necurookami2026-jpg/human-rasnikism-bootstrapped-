# Immanuel / Emanuel manual and planning studio

Version 0.1 · Rasniki collection revision

Immanuel and Emanuel are retained as the author's names for the manual systems. Their use here does not claim a religious identity or authority. Ostar is an author-supplied label for a proposed rawful lair edition. Meanings remain provisional, and this AI-assisted collection treats “max” as an expansion goal.

## Implemented software

Open manuals.html. The studio generates structured manuals and advocacy plans, performs explicit literal text replacement, creates bounded K0 console programs, and validates dependency blueprints. These are deterministic tools, not an AI rewriting service, an architectural approval system, or a general-purpose programming IDE.

The manual builder includes purpose, audience, procedure, acceptance criteria, rights and boundaries, declared locations, and unresolved review questions. Modes are Immanuel manual, Emanuel manual, advocacy, strategy/stragego, Ostar makkakah, Ostar aantonymmakkakah, and jurisdiction review. Changing modes changes prompts and review wording, not the legal or scientific status of an output.

## Manual systems

A manual states what the procedure is for, who may use it, what resources it needs, how to carry it out, what success looks like, and when to stop or seek review. Immanuel and Emanuel are two named entry points to the same implemented manual format; no unsupported technical distinction is invented between them.

## Advocacy

The advocacy mode organizes an issue, its affected audience, evidence, requested remedy, lawful participation routes, and review. Advocacy should distinguish facts, allegations, and opinions; avoid fabricated support or impersonation; and preserve room for correction and disagreement. The software does not contact people, lobby officials, run campaigns, or verify factual claims.

## Rewriting

Literal replacement replaces every occurrence of a supplied nonempty string in working text. It is case-sensitive, uses no regular expressions, and never evaluates code. Review the result before exporting. A successful replacement does not establish accuracy, good style, consent, or publication rights. Inputs and output are bounded to 100,000 UTF-16 units. A new rewrite replaces the preview, not the original input.

## Reprogramming

The K0 source generator converts an entered message into mark and signal instructions that emit its UTF-8 bytes, followed by the declared stop-port operation. The message is limited to 4095 encoded bytes so the program fits in K0 memory. Use the existing Python assembler and interpreter to assemble and run it. This is a bounded program-generation tool, not arbitrary software modification, native machine code, or code executed automatically in the browser.

## Blueprint, architect, and structures

Enter one component per line as `id | title | dependency1, dependency2`. IDs use letters, digits, hyphens, or underscores. The validator rejects duplicate IDs, undefined dependencies, self-dependencies, and dependency cycles. It exports a JSON blueprint with a dependency-first construction order.

Limits are 100 components, 10,000 input characters, 80 characters per ID, and 300 characters per title. The ordering is a software planning utility. It provides no structural engineering, building approval, cost assurance, code-compliance certification, or physical construction design.

## Strategy / stragego

The strategy mode records a goal, alternatives, assumptions, resources, decision criteria, and a review point through the common manual fields. It does not optimize decisions automatically or guarantee outcomes. Stragego is retained as a supplied spelling alongside strategy.

## Ostar rawful lair editions

Ostar makkakah sustains a useful lair practice through observation, care, and review. Ostar aantonymmakkakah reconsiders its framing and opens a route to repair. Neither variant erases the existing Rasniki or Blue editions. These are constructive, voluntary fictional frameworks, not territorial claims or supernatural interventions.

## Jurisdiction review edition

The jurisdiction mode keeps an unreviewed status and requests applicable-law analysis, current authoritative sources, rights and permissions, and an appropriate reviewer. Declared locations alone do not determine governing law. The software cannot make a document legally valid by rewriting it or by selecting a location.

The earlier jurisdiction tool remains available. No verified legal rule database, legal professional review, authenticated agreement, or automatic compliance engine has been added by this edition.

## Collection integration and checks

The collection index now links these tools alongside the lore, software kit, catalogue, search, I/O, Archangel management, game, and systematics. Earlier editions retain their source documents and limitations; this revision expands and checks the collection rather than deleting its history.

Run `node software/test_manuals.cjs`. Relevant checks cover builder fields, mode validation, bounded replacement, UTF-8 source generation, dependency ordering, malformed and cyclic blueprints, and basic UI behavior. Run the generated source through the K0 toolchain to verify the emitted message. No check certifies legal validity or professional architectural work.
