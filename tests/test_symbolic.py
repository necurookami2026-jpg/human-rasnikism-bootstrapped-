"""Consent, bounded input, inert text and explicit documentation comparisons."""
import copy
import json
import unittest
from unittest.mock import patch

from madrigal_lab import symbolic


def example():
    return {'archetype': 'wizardry', 'title': 'A fictional reading circle',
            'purpose': 'Reflect on a story and its declared limits.', 'reflection': 'I can revise this narrative.',
            'consent': True, 'opt_out': False, 'accessibility': 'Plain text and optional breaks.',
            'withdrawal': 'Stop and discard the client form at any time.',
            'support': {criterion['id']: 'A supplied documentation statement.'
                        for criterion in symbolic.catalogue()['criteria']}}


class SymbolicTests(unittest.TestCase):
    def test_complete_partial_and_absent_documentation_scores(self):
        record = example()
        complete = symbolic.evaluate(record)
        self.assertEqual((complete['rubric']['score'], complete['rubric']['max_score']), (6, 6))
        self.assertFalse(complete['rubric']['effect_verified'])
        self.assertEqual(complete['rubric']['evidence_status'], 'unverified-reference-present')
        del record['support']['implementation']
        del record['support']['evidence']
        documented = symbolic.evaluate(record)
        self.assertEqual(documented['rubric']['score'], 4)
        self.assertEqual(documented['rubric']['missing_support'], ['implementation', 'evidence'])
        record['support'] = {}
        absent = symbolic.evaluate(record)
        self.assertEqual(absent['rubric']['score'], 0)
        self.assertEqual(absent['rubric']['support_status'], 'absent-support')

    def test_comparison_uses_explicit_documentation_baselines(self):
        result = symbolic.compare(example())
        comparison = result['comparison']
        self.assertEqual(comparison['submitted_score'], 6)
        self.assertEqual(comparison['documentation_only_score'], 4)
        self.assertEqual(comparison['absent_support_score'], 0)
        self.assertEqual(comparison['implementation_evidence_delta'], 2)
        self.assertEqual(comparison['absent_support_delta'], 6)
        self.assertTrue(comparison['unverified'])
        record = example()
        record['support'] = {'evidence': 'Unresolved user-supplied reference.'}
        comparison = symbolic.compare(record)['comparison']
        self.assertEqual((comparison['submitted_score'], comparison['documentation_only_score']), (1, 0))

    def test_explicit_boolean_consent_and_opt_out_are_required(self):
        for value in (False, None, 0, 1, 'true', 'false'):
            record = example()
            record['consent'] = value
            with self.subTest(consent=value), self.assertRaises(ValueError):
                symbolic.evaluate(record)
        record = example()
        del record['consent']
        with self.assertRaises(ValueError):
            symbolic.compare(record)
        for value in (True, 0, 1, None, 'false'):
            record = example()
            record['opt_out'] = value
            with self.subTest(opt_out=value), self.assertRaises(ValueError):
                symbolic.evaluate(record)
        record = example()
        del record['opt_out']
        with self.assertRaises(ValueError):
            symbolic.evaluate(record)

    def test_known_archetypes_and_explicit_spelling_aliases(self):
        catalogue = symbolic.catalogue()
        self.assertEqual(len(catalogue['archetypes']), 5)
        for archetype in catalogue['archetypes']:
            record = example()
            record['archetype'] = archetype['id']
            result = symbolic.evaluate(record)
            self.assertEqual(result['record']['archetype'], archetype['id'])
            self.assertTrue(result['boundaries']['fictional_worldbuilding'])
        for alias in ('thaumatugy', 'THAUMATURGRY', 'thaumturgy'):
            record = example()
            record['archetype'] = alias
            result = symbolic.evaluate(record)
            self.assertEqual(result['record']['archetype'], 'thaumaturgy')
            self.assertTrue(result['archetype_resolution']['spelling_alias_used'])
        record['archetype'] = 'undeclared-real-power'
        with self.assertRaises(ValueError):
            symbolic.evaluate(record)

    def test_utf8_byte_bounds_empty_titles_and_whitespace_support(self):
        record = example()
        record['reflection'] = '🌿' * 1000
        self.assertEqual(symbolic.evaluate(record)['record']['reflection'], record['reflection'])
        record['reflection'] += '🌿'
        with self.assertRaises(ValueError):
            symbolic.evaluate(record)
        for field, value in (('title', ' '), ('purpose', '\n'), ('withdrawal', 'x' * 1001), ('reflection', 42)):
            record = example()
            record[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                symbolic.evaluate(record)
        record = example()
        record['support'] = {'evidence': '\n  \t'}
        self.assertEqual(symbolic.evaluate(record)['rubric']['score'], 0)
        record['support']['evidence'] = 'x' * 2001
        with self.assertRaises(ValueError):
            symbolic.evaluate(record)

    def test_unknown_targets_and_typed_support_are_rejected(self):
        for field in ('enemy_target', 'permanent_guarantee', 'remote_url'):
            record = example()
            record[field] = 'unsupported operational instruction'
            with self.subTest(field=field), self.assertRaises(ValueError):
                symbolic.evaluate(record)
        for support in (True, [], {'unknown_criterion': 'text'}, {'implementation': True}):
            record = example()
            record['support'] = support
            with self.subTest(support=support), self.assertRaises(ValueError):
                symbolic.evaluate(record)

    def test_supplied_code_and_references_remain_inert_without_io(self):
        record = example()
        record['reflection'] = '__import__("os").system("echo should never execute")'
        record['support']['evidence'] = 'https://example.invalid/not-resolved; /etc/passwd not read'
        with patch('builtins.open', side_effect=AssertionError('No file I/O')), \
             patch('socket.socket', side_effect=AssertionError('No network I/O')):
            result = symbolic.compare(record)
        self.assertEqual(result['record']['reflection'], record['reflection'])
        self.assertEqual(result['record']['support']['evidence'], record['support']['evidence'])
        self.assertFalse(result['boundaries']['source_execution'])
        self.assertFalse(result['participation']['server_retention'])

    def test_deterministic_results_do_not_mutate_inputs_or_catalogue(self):
        record = example()
        original = copy.deepcopy(record)
        first = symbolic.compare(record)
        second = symbolic.compare(record)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(record, original)
        first['record']['support']['evidence'] = 'changed returned data'
        self.assertEqual(record, original)
        catalogue = symbolic.catalogue()
        catalogue['archetypes'].clear()
        catalogue['aliases'].clear()
        self.assertEqual(len(symbolic.catalogue()['archetypes']), 5)
        self.assertEqual(symbolic.catalogue()['aliases']['thaumatugy'], 'thaumaturgy')


if __name__ == '__main__':
    unittest.main()
