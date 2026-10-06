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

COMPONENTS = [
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
    ('curriculum', 'implemented', 'Five exercises with stated acceptance evidence'),
    ('franchise', 'proposed', 'Derivative manifest and version/authority record; no rights granted'),
    ('sovereignty', 'editorial', 'Fictional governance notes with no grant of political authority'),
]
CURRICULUM = [
    {'cycle': 'Object', 'exercise': 'Compile emit "care", then round-trip its assembly.', 'evidence': 'Equal bytecode before and after canonical formatting.'},
    {'cycle': 'Room', 'exercise': 'Write and read a local document; attempt a parent-directory escape.', 'evidence': 'Text round-trip succeeds and escape is rejected.'},
    {'cycle': 'Household', 'exercise': 'Create a practice and record continuation, review and release.', 'evidence': 'Permitted state transitions with persisted history.'},
    {'cycle': 'Ashram', 'exercise': 'Create demo accounts, issue credits and transfer a portion.', 'evidence': 'Balanced postings, unchanged circulation after transfer, failed overdraw has no effect.'},
    {'cycle': 'Federation', 'exercise': 'Compare an explicitly trusted file baseline after editing a document.', 'evidence': 'Modified path is reported; scan findings remain indicators.'},
]


def catalogue():
    return {'version': '0.1.0', 'components': [{'id':i,'status':s,'scope':d} for i,s,d in COMPONENTS],
            'glossary': GLOSSARY, 'curriculum': CURRICULUM,
            'prototype': 'Python-hosted local lab', 'archetypes': ['maintainer', 'reviewer', 'learner', 'steward'],
            'paradigms': ['bounded execution', 'explicit evidence', 'versioned repair', 'double-entry accounting'],
            'scope': 'Finite tools and simulations; no universal exact-science or native-sovereignty claim'}
