"""Finite exact-label atlas, bounded advice tree and documentary family samplers.

Only the reviewed local catalogue is read. No supplied labels become code,
authorization rules, scientific claims or remote actions. Returned metadata is
fresh data so a client cannot alter the shared catalogue through mutation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import deque
from functools import lru_cache
from pathlib import Path


_SOURCE = Path(__file__).resolve().parents[1] / 'docs' / 'REQUESTED-SYSTEMS.json'
_KINDS = frozenset(('advice', 'guidance', 'manual', 'inquiry', 'survey', 'quest',
                   'logistics', 'fandom', 'community', 'media', 'learning',
                   'preferences', 'map', 'radio', 'diary', 'contract', 'recipe',
                   'genealogy', 'research', 'health', 'record'))
_STATUSES = frozenset(('documentary-reference', 'editorial-governance-proposal',
                      'fictional-label-only', 'awaiting-author-definition',
                      'fictional-or-unresolved', 'official-owner-recovery-only',
                      'unresolved-expression-no-access-rule',
                      'implemented-record-framework',
                      'implemented-derived-quest-summary',
                      'simulated-demo-ledger', 'review-and-integrity-only'))


def _integer(value, name, lower, upper):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f'{name} must be an integer in {lower}..{upper}')
    return value


def _query(value):
    if not isinstance(value, str):
        raise ValueError('query must be text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError as error:
        raise ValueError('query must be valid UTF-8 text') from error
    if size > 512:
        raise ValueError('query exceeds 512 UTF-8 bytes')
    return value.strip().casefold()


@lru_cache(maxsize=1)
def _source():
    data = json.loads(_SOURCE.read_text(encoding='utf-8'))
    if data.get('format') != 'rasniki-requested-systems-atlas' or data.get('version') != 1:
        raise ValueError('Unsupported requested-systems atlas')
    records, categories = data['items'], data['categories']
    if not isinstance(records, list) or not 1 <= len(records) <= 2048:
        raise ValueError('Atlas inventory must contain 1..2048 finite records')
    category_ids = {record['id'] for record in categories}
    if len(category_ids) != len(categories):
        raise ValueError('Atlas category identifiers must be unique')
    labels, ids = set(), set()
    for record in records:
        label = record['label']
        identifier = 'term-' + hashlib.sha256(label.encode('utf-8')).hexdigest()[:16]
        if (record['id'] != identifier or label in labels or identifier in ids
                or record['category'] not in category_ids
                or any(category not in category_ids for category in record['categories'])
                or record['record_template'] not in _KINDS
                or record['status'] not in _STATUSES
                or type(record['occurrences']) is not int or record['occurrences'] < 1):
            raise ValueError('Invalid or duplicate atlas record')
        labels.add(label)
        ids.add(identifier)
    if records != sorted(records, key=lambda record: (record['label'].casefold(), record['label'])):
        raise ValueError('Atlas labels must use the declared stable sort order')
    if data['summary']['distinct_labels'] != len(records):
        raise ValueError('Atlas label summary does not match its records')
    return data


def _matches(record, query):
    if not query:
        return True
    text = ' '.join((record['label'], record['category'], record['status'],
                     record['scope'], record['record_template'],
                     *(alias['label'] for alias in record['alias_proposals'])))
    return query in text.casefold()


def catalogue(query='', limit=256, offset=0):
    """Search the finite inventory, returning at most 256 exact-label records."""
    query = _query(query)
    limit = _integer(limit, 'limit', 1, 256)
    offset = _integer(offset, 'offset', 0, 2048)
    source = _source()
    matches = [record for record in source['items'] if _matches(record, query)]
    selected = matches[offset:offset + limit]
    return {'format': 'rasniki-requested-systems-catalogue', 'version': 1,
            'query': query, 'offset': offset, 'limit': limit,
            'total': len(source['items']), 'matches': len(matches),
            'returned': len(selected), 'has_more': offset + len(selected) < len(matches),
            'items': copy.deepcopy(selected), 'categories': copy.deepcopy(source['categories']),
            'summary': dict(source['summary']), 'bounds': dict(source['bounds']),
            'coverage': source['coverage'], 'occurrence_basis': source['occurrence_basis'],
            'scope': 'Finite source labels and record templates; named products, hardware, powers and all recursive instances are not thereby implemented.'}


def tree(depth=3, limit=256, query=''):
    """Return a breadth-first finite tree with advice and guidance for each label.

    Root -> category -> exact label -> advice/guidance has four actual levels.
    A permitted depth of eight never creates extra copies or recursive content.
    Children in the response always refer to returned nodes; omitted-child
    counts distinguish this bounded view from the complete filtered tree.
    """
    depth = _integer(depth, 'depth', 0, 8)
    limit = _integer(limit, 'limit', 1, 256)
    query = _query(query)
    source = _source()
    matches = [record for record in source['items'] if _matches(record, query)]
    by_category = {category['id']: [] for category in source['categories']}
    for record in matches:
        by_category[record['category']].append(record)
    definitions = {'atlas': {'id': 'atlas', 'parent': None, 'depth': 0,
                            'kind': 'root', 'label': 'Finite requested-systems atlas',
                            'children': []}}
    for category in source['categories']:
        records = by_category[category['id']]
        if not records:
            continue
        category_id = 'category:' + category['id']
        definitions['atlas']['children'].append(category_id)
        definitions[category_id] = {'id': category_id, 'parent': 'atlas', 'depth': 1,
                                    'kind': 'category', 'label': category['label'],
                                    'scope': category['scope'],
                                    'children': [record['id'] for record in records]}
        for record in records:
            identifier = record['id']
            definitions[identifier] = {'id': identifier, 'parent': category_id,
                                      'depth': 2, 'kind': 'label', 'label': record['label'],
                                      'status': record['status'], 'scope': record['scope'],
                                      'occurrences': record['occurrences'],
                                      'crosslinks': list(record['crosslinks']),
                                      'record_template': record['record_template'],
                                      'children': [identifier + ':advice', identifier + ':guidance']}
            for kind, text in (('advice', record['advice']),
                               ('guidance', '\n'.join(record['guidance']))):
                child_id = identifier + ':' + kind
                definitions[child_id] = {'id': child_id, 'parent': identifier,
                                         'depth': 3, 'kind': kind,
                                         'label': kind.capitalize() + ' for ' + record['label'],
                                         'text': text, 'children': []}
    pending, eligible = deque(['atlas']), []
    while pending:
        identifier = pending.popleft()
        node = definitions[identifier]
        if node['depth'] > depth:
            continue
        eligible.append(node)
        pending.extend(node['children'])
    selected = copy.deepcopy(eligible[:limit])
    returned_ids = {node['id'] for node in selected}
    for node in selected:
        original_children = node['children']
        node['children'] = [child for child in original_children if child in returned_ids]
        node['omitted_children'] = len(original_children) - len(node['children'])
    return {'format': 'rasniki-requested-systems-tree', 'version': 1,
            'query': query, 'depth_budget': depth, 'limit': limit,
            'matching_labels': len(matches), 'total_available_nodes': len(eligible),
            'returned_nodes': len(selected), 'truncated': len(eligible) > limit,
            'nodes': selected,
            'scope': 'Finite catalogue branches with voluntary advice/review prompts; no infinite expansion or instructions to override authority.'}


def families():
    """Keep requested governance titles distinct from a proposed family completion."""
    source = _source()
    labels = {record['label']: record for record in source['items']}
    roles = ('amatriarch', 'amatriarchy', 'patriarch', 'patriarchy',
             'heirarch', 'heirararchy', 'aomniarch', 'aomniarchy',
             'matriarch', 'matriarchy', 'apatriarch', 'apatriarchy',
             'aheirarch', 'aheirararchy', 'omniarch', 'omniarchy')
    governance = []
    for era in ('original', 'classical'):
        for role in roles:
            label = era + ' ' + role
            requested = label in labels
            governance.append({'label': label, 'era': era, 'role_label': role,
                               'requested': requested,
                               'occurrences': labels[label]['occurrences'] if requested else 0,
                               'status': 'editorial-governance-proposal' if requested else 'proposed-family-completion',
                               'scope': 'Documentary title only; no appointment, legal or political authority.'})
    governance.sort(key=lambda record: (record['label'].casefold(), record['label']))
    hospitality = [copy.deepcopy(record) for record in source['items']
                   if record['category'] == 'fictional-food-and-hospitality'
                   and record['label'].split(' ', 1)[0] in
                   ('acid', 'water', 'milk', 'blood', 'sabbath', 'ambiotic', 'biotic')
                   and record['label'].split(' ', 1)[-1] in
                   ('drinks', 'soda', 'cafe', 'bistro', 'jacuzzi', 'spa', 'wine', 'saloon')]
    return {'format': 'rasniki-documentary-families', 'version': 1,
            'governance': governance, 'requested_governance_labels': sum(row['requested'] for row in governance),
            'proposed_governance_labels': sum(not row['requested'] for row in governance),
            'hospitality': hospitality, 'hospitality_labels': len(hospitality),
            'scope': 'Bounded documentary family views; proposed completion is explicitly absent from the original request and creates no operational systems.'}


def document_types(limit=32):
    """Sample proposed seven-way addresses; 7^7 potential leaves are not produced."""
    limit = _integer(limit, 'limit', 1, 256)
    addresses = []
    for index in range(limit):
        number, digits = index, [0] * 7
        for level in range(6, -1, -1):
            number, digits[level] = divmod(number, 7)
        addresses.append({'index': index, 'address': digits})
    return {'format': 'rasniki-proposed-document-type-addresses', 'version': 1,
            'source_label': 'my 7 amp 7 amp 7 amp 7 amp 7 amp 7 amp 7 document types',
            'interpretation': 'Proposed seven levels with seven branch choices per level; author semantics for amp remain unconfirmed.',
            'status': 'proposed-bounded-address-sampler', 'levels': 7, 'branches_per_level': 7,
            'potential_leaves': 7 ** 7, 'sampled_positions': limit,
            'addresses': addresses, 'documents_generated': 0, 'ops_executed': 0,
            'scope': 'Only finite numerical addresses are sampled; no assertion of 823543 existing documents, finality or universal document types.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='')
    parser.add_argument('--limit', type=int, default=32)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--tree', action='store_true')
    parser.add_argument('--depth', type=int, default=3)
    parser.add_argument('--families', action='store_true')
    parser.add_argument('--document-types', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.families:
            result = families()
        elif args.document_types:
            result = document_types(args.limit)
        elif args.tree:
            result = tree(args.depth, args.limit, args.query)
        else:
            result = catalogue(args.query, args.limit, args.offset)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
