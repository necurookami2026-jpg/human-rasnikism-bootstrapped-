"""Explicit terminology, capability status and curriculum for the virtual lab."""
from .language import MANIFEST

GLOSSARY = [
    {'term': m['name'], 'meaning': m['scope'], 'status': 'implemented-finite-mode',
     'fields': m['payload'], 'source': 'vendor/rasnikism/QUILT.md'} for m in MANIFEST['modes']
]
GLOSSARY += [
    {'term': 'counteramakkakah', 'meaning': 'Lab convention: read-only protective review preserving useful records.', 'status': 'proposed-convention', 'source': 'Rasniki-Monarchic-Charter.md'},
    {'term': 'counterantonymmakkakah', 'meaning': 'Explicit alias of the finite counterantonymmakkkah mode.', 'status': 'implemented-alias', 'source': 'vendor/rasnikism/SYSTEMATICS.md'},
    {'term': 'makkah', 'meaning': 'Lab alias for makkakah, subject to author confirmation.', 'status': 'provisional-alias', 'source': 'user spelling'},
    {'term': 'ainsuitable', 'meaning': 'Conformity to a declared specification; not a safety certification.', 'status': 'source-defined', 'source': 'vendor/rasnikism/KEROT.md'},
    {'term': 'suitable', 'meaning': 'Lab convention: acceptance criteria recorded with their checks.', 'status': 'proposed-convention', 'source': 'lab design'},
    {'term': 'recursive', 'meaning': 'Bounded repeated review or computation, with an explicit budget.', 'status': 'implemented-convention', 'source': 'lab design'},
    {'term': 'nomic', 'meaning': 'Versioned rule proposals reviewed before adoption; no automatic lawmaking.', 'status': 'proposed-convention', 'source': 'lab design'},
    {'term': 'emergency', 'meaning': 'Highest-priority simulated organiser item; no emergency service dispatch.', 'status': 'implemented-convention', 'source': 'lab design'},
    {'term': 'urgency', 'meaning': 'Second-priority simulated organiser item.', 'status': 'implemented-convention', 'source': 'lab design'},
    {'term': 'aurgency', 'meaning': 'User spelling retained as a provisional alias of urgency.', 'status': 'provisional-alias', 'source': 'user spelling'},
    {'term': 'sovereignty', 'meaning': 'Documented fictional governance concept; no state recognition or governmental power.', 'status': 'editorial', 'source': 'Rasniki-Monarchic-Charter.md'},
    {'term': 'heraldry', 'meaning': 'Local decorative emblem accompanying the collection.', 'status': 'implemented-artwork', 'source': 'madrigal_lab/web/heraldry.svg'},
    {'term': 'ashram', 'meaning': 'Voluntary learning and practice records within the lore.', 'status': 'source-defined', 'source': 'vendor/rasnikism/MAKKAKAH.md'},
    {'term': 'pseudo ROM', 'meaning': 'In-memory copy of validated K0 bytecode used for simulated boot.', 'status': 'implemented-simulation', 'source': 'lab design'},
]
for term in ('henapenall', 'counterabolshivik', 'counteraantonymbloshivik', 'bloshivik',
             'aaantonymbolshivik', 'counteraemergency', 'counterurgency', 'etceranative',
             'emrome', 'counteraaantonymspyware', 'counteraaantonymrandomware', 'counter noninterpretable software'):
    GLOSSARY.append({'term': term, 'meaning': None, 'status': 'awaiting-author-definition', 'source': 'user supplied label'})


# Publication labels are retained without inventing executable or political powers.
for term in ('hopput', 'aimat', 'sciencerainbow', 'finalisable catch', 'max greatest', 'omniarchy'):
    GLOSSARY.append({'term': term, 'meaning': 'Author-supplied publication label; no additional executable or governing semantics are established.', 'status': 'edition-label', 'source': 'user supplied edition title'})
GLOSSARY += [
    {'term': 'rawful', 'meaning': 'Direct construction with recorded derivations, as provisionally defined by the project.', 'status': 'source-defined', 'source': 'vendor/rasnikism/KEROT.md'},
    {'term': 'Kerot (Ministry)', 'meaning': 'Fictional craft of tracing how a change to a thread affects its pattern; distinct from executable K0.', 'status': 'fictional-worldbuilding', 'source': 'vendor/internetwomanagementministry/site/index.html'},
    {'term': 'Exact Final (Ministry)', 'meaning': 'A preserved version with a recorded boundary and keeper; exact does not mean universal perfection.', 'status': 'fictional-worldbuilding', 'source': 'vendor/internetwomanagementministry/site/index.html'},
    {'term': 'Final Quilt (Ministry)', 'meaning': 'The fictional living archive of accepted patterns, preserving versions while new branches grow.', 'status': 'fictional-worldbuilding', 'source': 'vendor/internetwomanagementministry/site/index.html'},
    {'term': 'Hensensual (Ministry)', 'meaning': 'Coined fictional mutual awareness among parts of a composite.', 'status': 'fictional-worldbuilding', 'source': 'vendor/internetwomanagementministry/site/index.html'},
    {'term': 'Penfinal (Ministry)', 'meaning': 'The fictional reviewable stage before acceptance into the archive.', 'status': 'fictional-worldbuilding', 'source': 'vendor/internetwomanagementministry/site/index.html'},
]


GLOSSARY += [
    {'term': 'lair', 'meaning': 'A chosen place of attention, rest, creation and return; here a bounded source or document container.', 'status': 'source-defined-with-editorial-application', 'source': 'vendor/rasnikism/LAIR.md'},
    {'term': 'formate', 'meaning': 'User spelling retained as an editorial label for the selected view of a recorded form; no new instruction.', 'status': 'proposed-presentation-label', 'source': 'docs/LAIR-OF-LAIRS.md'},
    {'term': 'sureasuch', 'meaning': None, 'status': 'awaiting-author-definition', 'source': 'user supplied label'},
    {'term': 'asuresuch', 'meaning': None, 'status': 'awaiting-author-definition', 'source': 'user supplied label'},
    {'term': 'surasuch', 'meaning': None, 'status': 'awaiting-author-definition', 'source': 'user supplied label'},
]

GLOSSARY += [
    {'term': 'asorcery', 'meaning': 'A fictional symbolic-reflection archetype in the voluntary workbench.', 'status': 'implemented-fictional-archetype', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'thaumaturgy', 'meaning': 'A fictional wonder-working narrative archetype; no measured supernatural ability is inferred.', 'status': 'implemented-fictional-archetype', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'thaumturgy', 'meaning': 'User spelling retained as an alias of the thaumaturgy archetype.', 'status': 'implemented-alias', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'wizardry', 'meaning': 'A fictional study and worldbuilding archetype.', 'status': 'implemented-fictional-archetype', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'Jedi-inspired', 'meaning': 'A fictional reflection archetype; no affiliation, endorsement or franchise rights are asserted.', 'status': 'implemented-fictional-archetype', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'asith-inspired', 'meaning': 'User label retained for a fictional reflection archetype; no affiliation, endorsement or franchise rights are asserted.', 'status': 'implemented-fictional-archetype', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'Easterbunny', 'meaning': 'Proposed local six-field documentation-presence rubric with transparent absent-support and documentation-only baselines.', 'status': 'implemented-proposed-rubric', 'source': 'madrigal_lab/symbolic.py'},
    {'term': 'nonexistenced', 'meaning': 'In this proposed rubric, the absent-support comparison contains no supplied supporting fields; no conclusion about people or beings.', 'status': 'proposed-comparison-label', 'source': 'docs/SPIRITUAL-SYMBOLIC-WORKBENCH.md'},
    {'term': 'spiritual sciences', 'meaning': 'Participant-chosen reflective subject label, with spiritual beliefs distinguished from tested software behavior.', 'status': 'editorial-scope', 'source': 'docs/SPIRITUAL-SYMBOLIC-WORKBENCH.md'},
]

COMPONENTS = [
    ('owned-media-studio', 'implemented-local', 'Browser-local audio/video playback, raster brightness/contrast/crop edits, owned-data fingerprints, original seed renditions and timed text-card WebM animatics'),
    ('recursive-systems-atlas', 'implemented-bounded', 'Sorted exact-label inventory, paginated search, finite advice/guidance trees and seven-way document address samples'),
    ('local-boards', 'implemented-local', 'Consented local inquiries, surveys, replies, parented records, reviewed quests and fictional leaderboards; no authenticated public membership'),
    ('workpapers', 'implemented-local', 'Ten prose rendering formats, deterministic original fictional seeds and manually supplied coordinate SVG plots'),
    ('owner-recovery', 'implemented-local', 'Official account recovery checklists and digest-checked exclusive local backup restoration; no password cracking or access bypass'),
    ('demo-obligations-contracts', 'simulated', 'Atomic DEMO_CREDIT loan/repayment records, zero-transfer coupon annotations and versioned local contract receipts'),
    ('symbolic-practice', 'implemented-local', 'Voluntary fictional-archetype reflection, bounded input review and deliberate client JSON export; no server retention'),
    ('easterbunny-rubric', 'implemented-proposed-rubric', 'Six supplied support fields compared with documentation-only and absent-input baselines; no effect or truth verification'),
    ('conflict-protection-library', 'editorial-templates', 'Finite consent, accessibility, civilian-support, de-escalation and review documents; no guaranteed perpetual protection'),
    ('language', 'implemented', 'K0 assembler, disassembler, canonical formatter, Ras script compiler and bounded interpreter'),
    ('quilt', 'implemented', 'Eight finite source-backed modes; Boolean inputs are user assertions'),
    ('recursive-exact-science', 'implemented-bounded', 'Boolean addition exhaustive suite and bounded interpreter runs; not universal scientific proof'),
    ('boot', 'simulated', 'Pseudo-ROM, MBR-shaped record and UEFI handoff trace; no disk writes or executable EFI image'),
    ('kernel', 'simulated', 'Cooperative job queue and task states in a Python host; no hardware isolation'),
    ('virtualisation', 'simulated', 'Fresh K0 memory per execution; emulated ISA rather than hardware hypervisor'),
    ('madrigal-os', 'simulated', 'Local web desktop and hosted services; upstream spells the proposed OS Magrigal'),
    ('files', 'implemented', 'Root-confined UTF-8 file explorer and document reader'),
    ('bots', 'implemented-bounded', 'Intranet read-only jobs and HTTPS internet fetch to operator-configured hosts'),
    ('defense', 'implemented-read-only', 'Unchanged Guardian scanner and explicit trusted-baseline comparison; no malware prevention/removal/decryption'),
    ('finance', 'simulated', 'Atomic DEMO_CREDIT double-entry ledger, accounts and circulation report'),
    ('domain-host', 'simulated', 'Persistent .lab name-to-document registry; no public DNS registration'),
    ('internet-server', 'local-only', 'HTTP desktop/API binds IPv4 loopback; public hosting and TLS termination not deployed'),
    ('game-server', 'implemented-local', 'Shared target game state available through the local API'),
    ('organiser', 'implemented', 'Persistent practice records, priority queue and reviewed rule revisions'),
    ('curriculum', 'implemented', 'Twelve exercises with stated acceptance evidence'),
    ('franchise', 'proposed', 'Derivative manifest and version/authority record; no rights granted'),
    ('sovereignty', 'editorial', 'Fictional governance notes with no grant of political authority'),
    ('ministry-archive', 'implemented-static', 'Retained fictional archive, seven-term search and four rotating story seeds; no account or ministry integration'),
    ('hopput-publication', 'implemented-publication', 'Sorted source locks, documentation, offline reader and reproducible source archive'),
]
CURRICULUM = [
    {'cycle': 'Object', 'exercise': 'Compile emit "care", then round-trip its assembly.', 'evidence': 'Equal bytecode before and after canonical formatting.'},
    {'cycle': 'Room', 'exercise': 'Write and read a local document; attempt a parent-directory escape.', 'evidence': 'Text round-trip succeeds and escape is rejected.'},
    {'cycle': 'Household', 'exercise': 'Create a practice and record continuation, review and release.', 'evidence': 'Permitted state transitions with persisted history.'},
    {'cycle': 'Ashram', 'exercise': 'Create demo accounts, issue credits and transfer a portion.', 'evidence': 'Balanced postings, unchanged circulation after transfer, failed overdraw has no effect.'},
    {'cycle': 'Federation', 'exercise': 'Compare an explicitly trusted file baseline after editing a document.', 'evidence': 'Modified path is reported; scan findings remain indicators.'},
    {'cycle': 'Symbolic practice', 'exercise': 'Compare an opted-in record with four documentation fields, then add implementation and evidence descriptions.', 'evidence': 'Support coverage rises from 4/6 to 6/6; absent baseline remains zero and opt-out rejects evaluation.'},
    {'cycle': 'Conflict review', 'exercise': 'Use a fictional disagreement to complete an access plan, de-escalation note and correction record.', 'evidence': 'Separate observed facts from interpretations, preserve opt-out, and record the next bounded review.'},
    {'cycle': 'Local boards', 'exercise': 'Create an opted-in survey, submit a choice, then review a fictional quest.', 'evidence': 'Survey submission totals and once-only reviewed quest points, with no identity or financial-value claim.'},
    {'cycle': 'Obligations', 'exercise': 'Fund a demo loan from an existing balance and repay it in two parts.', 'evidence': 'Preserved circulation, atomic postings, reconciled outstanding amounts and rejected overpayment.'},
    {'cycle': 'Owned backup', 'exercise': 'Compare a known document digest and restore it to a new local path.', 'evidence': 'Digest mismatch writes nothing; existing files and path escapes are rejected.'},
    {'cycle': 'Workpapers and maps', 'exercise': 'Render a lecture paper and plot a manually supplied hypothetical coordinate.', 'evidence': 'Retained prose inputs, escaped SVG label and explicit absence of live tracking.'},
    {'cycle': 'Owned media', 'exercise': 'Edit an owned raster image and form a short text-card plan from original book prose.', 'evidence': 'Local PNG export, bounded scene provenance, permission withdrawal stops previews, and a draft WebM without cinema-quality or bodily-change claims.'},
]


def catalogue():
    return {'version': '0.1.0', 'components': [{'id':i,'status':s,'scope':d} for i,s,d in sorted(COMPONENTS)],
            'glossary': sorted(GLOSSARY,key=lambda record:record['term'].casefold()), 'curriculum': CURRICULUM,
            'prototype': 'Python-hosted local lab', 'archetypes': ['maintainer', 'reviewer', 'learner', 'steward'],
            'paradigms': ['bounded execution', 'explicit evidence', 'versioned repair', 'double-entry accounting'],
            'scope': 'Finite tools and simulations; no universal exact-science or native-sovereignty claim'}
