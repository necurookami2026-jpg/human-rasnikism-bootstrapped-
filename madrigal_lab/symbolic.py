"""Pure bounded fictional reflection and documentation-review functions.

This module performs no filesystem or remote I/O, executes no supplied content,
and retains no reflections. Scores describe supplied documentation presence;
they establish no supernatural effects, authority or implementation correctness.
"""
from __future__ import annotations


_ARCHETYPES = (
    ('asorcery', 'Asorcery', 'Fictional symbolic reflection'),
    ('thaumaturgy', 'Thaumaturgy', 'Fictional wonder-working narrative'),
    ('wizardry', 'Wizardry', 'Fictional study and worldbuilding'),
    ('jedi-inspired', 'Jedi-inspired', 'Fictional reflection; no affiliation or endorsement'),
    ('asith-inspired', 'Asith-inspired', 'Fictional reflection; no affiliation or endorsement'),
)
_ALIASES = {'thaumatugy': 'thaumaturgy', 'thaumaturgry': 'thaumaturgy', 'thaumturgy': 'thaumaturgy'}
_CRITERIA = (
    ('scope_and_limits', 'Scope and limits', 'Describe the finite fictional practice and the limits of its claims.'),
    ('consent_and_accessibility', 'Consent and accessibility', 'Describe voluntary participation and access arrangements.'),
    ('withdrawal', 'Withdrawal and opt-out', 'Describe how a participant can stop, decline or withdraw.'),
    ('provenance', 'Provenance', 'Identify the source, author or revision of the supplied documentation.'),
    ('implementation', 'Implementation description', 'Describe supplied software or procedures; this declaration is not independently checked.'),
    ('evidence', 'Evidence references', 'Record observations or references; their existence and contents are not independently checked.'),
)
_LIMITS = {'archetype': 64, 'title': 160, 'purpose': 1000, 'reflection': 4000,
           'accessibility': 1000, 'withdrawal': 1000, 'support_field': 2000}
_FIELDS = frozenset(('archetype', 'title', 'purpose', 'reflection', 'consent', 'opt_out',
                     'accessibility', 'withdrawal', 'support'))
_CRITERION_IDS = frozenset(criterion[0] for criterion in _CRITERIA)


def catalogue() -> dict:
    """Return fresh form metadata for the proposed six-field Easterbunny rubric."""
    return {
        'format': 'rasniki-symbolic-catalogue', 'version': 1,
        'rubric_name': 'Easterbunny', 'max_score': len(_CRITERIA),
        'archetypes': [{'id': key, 'name': name, 'scope': scope} for key, name, scope in _ARCHETYPES],
        'criteria': [{'id': key, 'label': label, 'scope': scope} for key, label, scope in _CRITERIA],
        'aliases': dict(_ALIASES), 'limits': dict(_LIMITS),
        'scoring': 'One point per nonempty support field; every field is supplied text, not verified implementation or evidence.',
        'scope': 'Input documentation presence; no supernatural, safety or correctness certification.',
        'retention': 'No server retention. A client may offer an explicitly requested local JSON export.',
        'participation': 'Consent must be explicitly true and opt_out false before evaluation.',
        'non_affiliation': 'Jedi-inspired and Asith-inspired are fictional labels; no franchise affiliation or endorsement is claimed.',
    }


def _text(value, field: str, maximum: int, required: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f'{field}: expected bounded UTF-8 text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError as error:
        raise ValueError(f'{field}: expected valid UTF-8 text') from error
    if size > maximum:
        raise ValueError(f'{field}: exceeds {maximum} UTF-8 bytes')
    if required and not value.strip():
        raise ValueError(f'{field}: nonempty text is required')
    return value


def _boolean(value, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f'{field}: expected a JSON boolean without coercion')
    return value


def _normalise(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError('A reflection record must be an object')
    unknown = set(record) - _FIELDS
    if unknown:
        raise ValueError('Unsupported record fields: ' + ', '.join(sorted(str(field) for field in unknown)))
    supplied_archetype = _text(record.get('archetype', ''), 'archetype', _LIMITS['archetype'], required=True)
    key = supplied_archetype.strip().lower()
    archetype = _ALIASES.get(key, key)
    if archetype not in {item[0] for item in _ARCHETYPES}:
        raise ValueError('Choose a declared fictional archetype')
    support = record.get('support', {})
    if not isinstance(support, dict) or set(support) - _CRITERION_IDS:
        raise ValueError('Support must contain only the six declared rubric fields')
    result = {'archetype': archetype,
              'consent': _boolean(record.get('consent', False), 'consent'),
              'opt_out': _boolean(record.get('opt_out'), 'opt_out')}
    for field in ('title', 'purpose', 'reflection', 'accessibility', 'withdrawal'):
        result[field] = _text(record.get(field, ''), field, _LIMITS[field], required=field in ('title', 'purpose'))
    result['support'] = {key: _text(support.get(key, ''), 'support.' + key, _LIMITS['support_field'])
                         for key, _label, _scope in _CRITERIA}
    if result['consent'] is not True:
        raise ValueError('Voluntary consent must be explicitly true before evaluation')
    if result['opt_out'] is not False:
        raise ValueError('Opt-out or withdrawal prevents evaluation')
    return result


def _rubric(support: dict) -> dict:
    criteria = [{'id': key, 'label': label, 'documented': bool(support[key].strip()),
                 'points': int(bool(support[key].strip()))} for key, label, _scope in _CRITERIA]
    score = sum(item['points'] for item in criteria)
    return {
        'name': 'Easterbunny', 'status': 'proposed-local-documentation-rubric',
        'score': score, 'max_score': len(_CRITERIA), 'criteria': criteria,
        'support_status': 'all-six-fields-present' if score == len(_CRITERIA) else 'partially-documented' if score else 'absent-support',
        'missing_support': [item['id'] for item in criteria if not item['documented']],
        'implementation_status': 'documented-unverified-claim' if support['implementation'].strip() else 'absent-description',
        'evidence_status': 'unverified-reference-present' if support['evidence'].strip() else 'absent-reference',
        'rule': 'Each nonempty support field earns one point. Text length and spiritual beliefs confer no extra points.',
        'effect_verified': False,
        'limits': 'Presence alone does not establish accuracy, completeness, quality, implementation correctness or supernatural effects.',
    }


def evaluate(record: dict) -> dict:
    """Validate voluntary input and score six documentation fields without I/O."""
    normalised = _normalise(record)
    supplied = record['archetype']
    return {
        'format': 'rasniki-symbolic-documentation-review', 'version': 1,
        'record': normalised,
        'archetype_resolution': {'supplied': supplied, 'canonical': normalised['archetype'],
                                'spelling_alias_used': supplied.strip().lower() in _ALIASES},
        'rubric': _rubric(normalised['support']),
        'participation': {'consent': True, 'opt_out': False, 'status': 'reported-voluntary-participation',
                          'accessibility': normalised['accessibility'], 'withdrawal': normalised['withdrawal'],
                          'independently_authenticated': False, 'server_retention': False},
        'boundaries': {'fictional_worldbuilding': True, 'supernatural_effects_verified': False,
                       'enemy_targeting': False, 'permanent_guarantee': False,
                       'remote_io': False, 'source_execution': False,
                       'non_affiliation': 'No affiliation or endorsement by any fictional franchise or rights holder is claimed.'},
    }


def compare(record: dict) -> dict:
    """Compare supplied documentation against two explicitly absent baselines.

The documentation-only baseline retains the first four support fields and
clears implementation/evidence descriptions. The absent-support baseline
clears all six. Neither baseline represents a person, belief or real system.
"""
    result = evaluate(record)
    support = result['record']['support']
    documentation_only = dict(support)
    documentation_only.update(implementation='', evidence='')
    absent = {key: '' for key in support}
    submitted_score = result['rubric']['score']
    documentation_only_rubric = _rubric(documentation_only)
    absent_rubric = _rubric(absent)
    result['comparison'] = {
        'scope': 'Supplied documentation text compared with explicit missing-support projections; no beliefs or people are ranked.',
        'submitted_score': submitted_score,
        'documentation_only_score': documentation_only_rubric['score'],
        'absent_support_score': absent_rubric['score'],
        'implementation_evidence_delta': submitted_score - documentation_only_rubric['score'],
        'absent_support_delta': submitted_score - absent_rubric['score'],
        'documentation_only': documentation_only_rubric,
        'absent_support': absent_rubric,
        'unverified': True,
    }
    return result
