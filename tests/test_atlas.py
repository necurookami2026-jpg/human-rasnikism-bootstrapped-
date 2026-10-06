"""Finite source coverage, deterministic pagination and bounded documentary views."""
import hashlib
import json
import unittest
from pathlib import Path

from madrigal_lab import atlas


class AtlasTests(unittest.TestCase):
    def all_records(self):
        return [record for offset in (0, 256, 512)
                for record in atlas.catalogue(limit=256, offset=offset)['items']]

    def test_full_sorted_pagination_retains_distinct_labels_and_repetitions(self):
        records = self.all_records()
        labels = [record['label'] for record in records]
        self.assertEqual(len(labels), 630)
        self.assertEqual(len(set(labels)), len(labels))
        self.assertEqual(labels, sorted(labels, key=lambda label: (label.casefold(), label)))
        self.assertTrue(atlas.catalogue()['has_more'])
        self.assertFalse(atlas.catalogue(offset=512)['has_more'])
        self.assertEqual(atlas.catalogue(offset=2048)['items'], [])
        summary = atlas.catalogue()['summary']
        self.assertEqual((summary['label_mentions'], summary['retained_label_mentions'],
                          summary['explicit_component_labels']), (649, 621, 28))
        self.assertFalse(summary['infinite_instances_generated'])
        lookup = {record['label']: record for record in records}
        for label in ('agency', 'chess', 'community ecosystem', 'gifs', 'photos',
                      'registry', 'revenant', 'sakerails', 'classical heirarch'):
            self.assertEqual(lookup[label]['occurrences'], 2)

    def test_unusual_named_labels_and_exact_spellings_are_preserved(self):
        labels = {record['label'] for record in self.all_records()}
        expected = {'immanuel', 'emmanuel', 'im manuel', 'im manue', 'womandeanamandean',
                    'ace thou', 'ayou this', 'as', 'am', 'are', 'ais', 'aid', 'we',
                    'they', 'she', 'u', 'thee', 'ai', 'ahe', 'athem', 'ame', 'ahow',
                    'hot', 'awho', 'tho', 'awhat', 'that', 'awhen', 'then', 'awhere',
                    'there', 'awhy', 'thy', 'matrirchy and omniarchy box office',
                    'heirarchy omniarchy box office', 'beirarchy patriarchy box office',
                    'patriarchy matriarchy box office', 'surasuch', 'sho[ppinglist',
                    'rasniki prference servicces', 'dichtomic matchersawatchers',
                    'spaceamice (physical)', 'limeatime (temporal)',
                    'matterashatter (adaptational)', 'fandom numer sayer',
                    'fandom seed merchandise', 'merchandise(goods) aka organs lessons im manue',
                    'my 7 amp 7 amp 7 amp 7 amp 7 amp 7 amp 7 document types'}
        self.assertTrue(expected <= labels, sorted(expected - labels))

    def test_query_is_literal_casefolded_bounded_and_aliases_are_proposals(self):
        found = atlas.catalogue('  IMMANUEL  ')
        self.assertEqual([record['label'] for record in found['items']], ['immanuel'])
        aliases = atlas.catalogue('calendar')['items']
        record = next(record for record in aliases if record['label'] == 'calender')
        self.assertEqual(record['alias_proposals'],
                         [{'label': 'calendar', 'status': 'proposed-spelling-alias', 'applied': False}])
        self.assertEqual(atlas.catalogue('<script>alert(1)</script>')['matches'], 0)
        for value in (None, {}, 7, '\ud800', 'x' * 513, '🧵' * 129):
            with self.subTest(query=repr(value)), self.assertRaises(ValueError):
                atlas.catalogue(value)

    def test_all_views_reject_boolean_coercion_and_excessive_budgets(self):
        for value in (True, False, 0, -1, 257, 1.0, '1', None):
            for operation in (atlas.catalogue, atlas.tree, atlas.document_types):
                with self.subTest(operation=operation.__name__, limit=value), self.assertRaises(ValueError):
                    operation(limit=value)
        for value in (True, -1, 9, 1.0, '3', None):
            with self.subTest(depth=value), self.assertRaises(ValueError):
                atlas.tree(depth=value)
        for value in (True, -1, 2049, '0', 0.0):
            with self.subTest(offset=value), self.assertRaises(ValueError):
                atlas.catalogue(offset=value)

    def test_tree_returns_reachable_parents_and_advice_with_omission_counts(self):
        result = atlas.tree(query='immanuel', depth=8)
        nodes = {node['id']: node for node in result['nodes']}
        self.assertEqual(len(nodes), 5)
        self.assertEqual({node['kind'] for node in nodes.values()},
                         {'root', 'category', 'label', 'advice', 'guidance'})
        self.assertFalse(result['truncated'])
        for node in nodes.values():
            if node['parent'] is not None:
                self.assertIn(node['parent'], nodes)
                self.assertIn(node['id'], nodes[node['parent']]['children'])
            self.assertTrue(set(node['children']) <= set(nodes))
            self.assertEqual(node['omitted_children'], 0)
        advice = next(node for node in nodes.values() if node['kind'] == 'advice')
        self.assertIn('immanuel', advice['text'])
        limited = atlas.tree(limit=1)
        self.assertTrue(limited['truncated'])
        self.assertEqual(limited['nodes'][0]['children'], [])
        self.assertEqual(limited['nodes'][0]['omitted_children'], 22)
        root_only = atlas.tree(depth=0)
        self.assertEqual(root_only['returned_nodes'], 1)
        self.assertFalse(root_only['truncated'])
        absent = atlas.tree(query='no such unique atlas label')
        self.assertEqual(absent['matching_labels'], 0)
        self.assertEqual(absent['nodes'][0]['children'], [])

    def test_governance_completion_is_distinguished_from_all_requested_titles(self):
        result = atlas.families()
        self.assertEqual((result['requested_governance_labels'], result['proposed_governance_labels']), (28, 4))
        proposed = {row['label'] for row in result['governance'] if not row['requested']}
        self.assertEqual(proposed, {'classical apatriarch', 'classical apatriarchy',
                                   'classical aheirarch', 'classical aheirararchy'})
        self.assertTrue(all(row['occurrences'] == 0 for row in result['governance'] if not row['requested']))
        self.assertTrue(all(row['status'] == 'proposed-family-completion'
                            for row in result['governance'] if not row['requested']))
        self.assertEqual(sum(row['occurrences'] for row in result['governance']), 32)

    def test_all_56_hospitality_labels_remain_fictional_names(self):
        result = atlas.families()
        expected = {prefix + ' ' + suffix
                    for prefix in ('acid', 'water', 'milk', 'blood', 'sabbath', 'ambiotic', 'biotic')
                    for suffix in ('drinks', 'soda', 'cafe', 'bistro', 'jacuzzi', 'spa', 'wine', 'saloon')}
        self.assertEqual(result['hospitality_labels'], 56)
        self.assertEqual({row['label'] for row in result['hospitality']}, expected)
        self.assertTrue(all(row['status'] == 'fictional-label-only' for row in result['hospitality']))
        self.assertTrue(all('no chemical or bodily-fluid recipes' in row['scope']
                            for row in result['hospitality']))

    def test_sensitive_names_never_become_universal_access_or_truth_rules(self):
        lookup = {record['label']: record for record in self.all_records()}
        for label in ('password decipherer', 'spftware to deblock anyone from being blocked',
                      'vaultception decipherer software', 'light decryption', 'radio decryption'):
            self.assertEqual(lookup[label]['status'], 'official-owner-recovery-only')
            self.assertIn('no password guessing', lookup[label]['scope'])
        for label in ('nonacess = acess', 'access = nonacess'):
            self.assertEqual(lookup[label]['status'], 'unresolved-expression-no-access-rule')
            self.assertIn('never applied as an authorization rule', lookup[label]['scope'])
        self.assertIn('truth is not automatically verified', lookup['testimony verifier']['scope'])
        self.assertEqual(lookup['smg']['status'], 'fictional-or-unresolved')

    def test_seven_way_sampler_generates_only_unique_bounded_addresses(self):
        result = atlas.document_types(256)
        self.assertEqual((result['potential_leaves'], result['sampled_positions'],
                          result['documents_generated'], result['ops_executed']), (823543, 256, 0, 0))
        addresses = [row['address'] for row in result['addresses']]
        self.assertEqual(len({tuple(address) for address in addresses}), 256)
        self.assertEqual(addresses[0], [0] * 7)
        self.assertEqual(addresses[49], [0, 0, 0, 0, 1, 0, 0])
        for row in result['addresses']:
            self.assertEqual(len(row['address']), 7)
            self.assertTrue(all(0 <= digit < 7 for digit in row['address']))
            index = 0
            for digit in row['address']:
                index = index * 7 + digit
            self.assertEqual(index, row['index'])
        self.assertIn('unconfirmed', result['interpretation'])

    def test_returns_are_independent_and_source_bytes_are_unchanged(self):
        path = Path(__file__).resolve().parents[1] / 'docs' / 'REQUESTED-SYSTEMS.json'
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        first = atlas.catalogue('immanuel')
        first['items'][0]['guidance'].append('client mutation')
        first['items'][0]['label'] = 'changed'
        first['categories'][0]['id'] = 'changed'
        second = atlas.catalogue('immanuel')
        self.assertEqual(second['items'][0]['label'], 'immanuel')
        self.assertNotIn('client mutation', second['items'][0]['guidance'])
        self.assertNotEqual(second['categories'][0]['id'], 'changed')
        first_tree = atlas.tree(query='immanuel')
        first_tree['nodes'][0]['children'].clear()
        self.assertTrue(atlas.tree(query='immanuel')['nodes'][0]['children'])
        first_family = atlas.families()
        first_family['hospitality'][0]['guidance'].clear()
        self.assertTrue(atlas.families()['hospitality'][0]['guidance'])
        self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(json.loads(path.read_text())['summary']['distinct_labels'], 630)


if __name__ == '__main__':
    unittest.main()
