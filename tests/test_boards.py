"""Persistent local workflows, anonymous submissions and bounded recursion."""
from concurrent.futures import ThreadPoolExecutor
import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from madrigal_lab.boards import BoardStore, KINDS, MAX_DEPTH, MAX_INTERACTIONS, MAX_RECORDS


def record(kind='inquiry', **fields):
    result = {'kind': kind, 'title': 'A supplied local question',
              'body': 'Choose a next step together.', 'consent': True}
    if kind == 'survey':
        result['options'] = ['Read together', 'Ask for a break']
    result.update(fields)
    return result


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'boards.sqlite3'
        self.store = BoardStore(self.path)

    def tearDown(self):
        self.directory.cleanup()

    def test_records_and_replies_persist_as_inert_supplied_text(self):
        payload = record(metadata={'unverified_reference': 'https://example.invalid', 'location': [51.5, -0.1]},
                         body='<script>throw "never executed"</script>')
        original = copy.deepcopy(payload)
        item = self.store.create(payload)
        self.assertEqual(payload, original)
        self.assertEqual(item['member_alias'], 'anonymous')
        reply = self.store.reply(item['id'], '__import__("os").system("never run")', True)
        reopened = BoardStore(self.path)
        saved = reopened.get(item['id'])
        self.assertEqual(saved['body'], payload['body'])
        self.assertEqual(saved['replies'][0]['id'], reply['id'])
        self.assertEqual(saved['replies'][0]['member_alias'], 'anonymous')
        item['metadata']['location'].append(999)
        self.assertEqual(reopened.get(item['id'])['metadata']['location'], [51.5, -0.1])

    def test_all_declared_kinds_are_records_and_health_is_not_a_diagnosis(self):
        for kind in KINDS:
            created = self.store.create(record(kind))
            self.assertEqual(self.store.list(kind)[0]['id'], created['id'])
        health = self.store.list('health')[0]
        self.assertIn('no diagnosis', health['scope'])
        self.assertNotIn('diagnosis', health)
        self.assertNotIn('personality', self.store.list('preferences')[0])
        self.assertEqual(len(self.store.list()), len(KINDS))
        with self.assertRaises(ValueError):
            self.store.list('undeclared-remote-chat')

    def test_every_mutation_requires_strict_boolean_consent(self):
        inquiry = self.store.create(record())
        survey = self.store.create(record('survey'))
        quest = self.store.create(record('quest'))
        for consent in (False, None, 0, 1, 'true', 'false', [], {}):
            actions = (
                lambda: self.store.create(record(consent=consent)),
                lambda: self.store.reply(inquiry['id'], 'Reply', consent),
                lambda: self.store.vote(survey['id'], 0, consent),
                lambda: self.store.transition(quest['id'], 'active', 'Start', consent),
                lambda: self.store.delete(inquiry['id'], consent),
            )
            for action in actions:
                with self.subTest(consent=consent), self.assertRaises(ValueError):
                    action()
        payload = record()
        del payload['consent']
        with self.assertRaises(ValueError):
            self.store.create(payload)
        self.assertEqual(len(self.store.list()), 3)
        self.assertEqual(self.store.get(inquiry['id'])['replies'], [])
        self.assertEqual(self.store.get(survey['id'])['survey']['submissions'], 0)
        self.assertEqual(self.store.get(quest['id'])['state'], 'open')

    def test_surveys_aggregate_submissions_without_claiming_unique_people(self):
        item = self.store.create(record('survey', options=['Plain text', 'Audio', 'Both']))
        for option, alias in ((0, 'anonymous'), (2, 'anonymous'), (2, 'reader'), (2, 'reader')):
            self.store.vote(item['id'], option, True, alias)
        result = self.store.get(item['id'])['survey']
        self.assertEqual([option['votes'] for option in result['options']], [1, 0, 3])
        self.assertEqual(result['submissions'], 4)
        self.assertFalse(result['verified_participants'])
        for option in (-1, 3, 8, True, False, 0.0, '1'):
            with self.subTest(option=option), self.assertRaises(ValueError):
                self.store.vote(item['id'], option, True)
        with self.assertRaises(ValueError):
            self.store.vote(self.store.create(record())['id'], 0, True)
        self.assertEqual(self.store.get(item['id'])['survey']['submissions'], 4)

    def test_survey_options_points_and_unknown_fields_are_validated_before_write(self):
        payloads = [record('survey', options=value) for value in (
            [], ['One'], list('123456789'), ['same', ' SAME '], ['One', ' '], ['One', 2], 'One,Two')]
        payloads.extend(record('quest', points=value) for value in (-1, 1001, True, 0.5, '10'))
        payloads.extend((record(points=10), record(options=[]), record(kind='undeclared'),
                         record(state='reviewed'), record(inferred_personality='certain')))
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.store.create(payload)
        self.assertEqual(self.store.list(), [])

    def test_quest_reviewed_points_are_fictional_and_count_only_once(self):
        first = self.store.create(record('quest', points=1000, member_alias='story-reader'))
        second = self.store.create(record('quest', points=20, member_alias='story-reader'))
        other = self.store.create(record('quest', points=12, member_alias='another-reader'))
        cancelled = self.store.create(record('quest', points=999))
        self.store.transition(cancelled['id'], 'cancelled', 'Participation withdrawn.', True)
        self.assertEqual(self.store.leaderboard()['entries'], [])
        awarded = 0
        for item in (first, second, other):
            self.store.transition(item['id'], 'active', 'Voluntarily started.', True)
            self.store.transition(item['id'], 'done', 'Supplied completion report.', True)
            self.assertEqual(sum(row['points'] for row in self.store.leaderboard()['entries']), awarded)
            reviewed = self.store.transition(item['id'], 'reviewed', 'Supplied local review.', True)
            self.assertFalse(reviewed['review_verified'])
            awarded += item['points']
        result = self.store.leaderboard()
        self.assertEqual(result['entries'], [
            {'member_alias': 'story-reader', 'points': 1020, 'reviewed_quests': 2},
            {'member_alias': 'another-reader', 'points': 12, 'reviewed_quests': 1},
        ])
        self.assertEqual(result['unit'], 'FICTIONAL_QUEST_POINT')
        self.assertFalse(result['financial_value'])
        self.assertFalse(result['verified_review'])
        with self.assertRaises(ValueError):
            self.store.transition(first['id'], 'reviewed', 'Duplicate review.', True)
        self.assertEqual(len(self.store.get(first['id'])['history']), 3)
        self.store.delete(first['id'], True)
        self.assertEqual(self.store.leaderboard()['entries'][0]['points'], 20)

    def test_invalid_transitions_leave_state_and_history_unchanged(self):
        quest = self.store.create(record('quest'))
        inquiry = self.store.create(record())
        for identifier, state, reason in (
                (quest['id'], 'done', 'Skipped start'), (quest['id'], 'reviewed', 'Skipped completion'),
                (quest['id'], 'active', ' '), (quest['id'], True, 'Wrong type'),
                (inquiry['id'], 'active', 'Not a quest')):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.store.transition(identifier, state, reason, True)
        self.assertEqual(self.store.get(quest['id'])['state'], 'open')
        self.assertEqual(self.store.get(quest['id'])['history'], [])
        self.store.transition(quest['id'], 'active', 'Start', True)
        self.store.transition(quest['id'], 'done', 'Complete', True)
        self.store.transition(quest['id'], 'active', 'Revise before review', True)
        self.assertEqual(self.store.get(quest['id'])['state'], 'active')

    def test_recursive_parent_and_display_bounds_and_leaf_deletion(self):
        root = self.store.create(record('guidance'))
        parent = root['id']
        for level in range(1, MAX_DEPTH):
            parent = self.store.create(record('manual', parent=parent, title='Level ' + str(level + 1)))['id']
        with self.assertRaises(ValueError):
            self.store.create(record(parent=parent))
        with self.assertRaises(ValueError):
            self.store.create(record(parent=999))
        with self.assertRaises(ValueError):
            self.store.delete(root['id'], True)
        tree = self.store.tree()
        self.assertEqual((tree['returned_records'], tree['truncated']), (8, False))
        limited = self.store.tree(depth=3)
        self.assertEqual((limited['returned_records'], limited['truncated']), (3, True))
        limited = self.store.tree(limit=2)
        self.assertEqual((limited['returned_records'], limited['truncated']), (2, True))
        self.assertEqual(self.store.tree(parent=parent)['roots'][0]['id'], parent)
        for arguments in ({'depth': True}, {'depth': 9}, {'depth': 0}, {'limit': True}, {'limit': 257}, {'limit': 0}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.store.tree(**arguments)
        self.store.reply(parent, 'A removable local reply', True)
        removed = self.store.delete(parent, True)
        self.assertEqual(removed['deleted_replies'], 1)
        replacement = self.store.create(record(parent=root['id']))
        self.assertGreater(replacement['id'], parent)
        with self.assertRaises(ValueError):
            self.store.get(parent)

    def test_utf8_bounds_and_bounded_finite_json_metadata(self):
        payload = record(title='🌿' * 40, body='🌿' * 2000)
        self.store.create(payload)
        invalid = [record(title='🌿' * 41), record(body='🌿' * 2001), record(title=' '),
                   record(body='\x00'), record(metadata=[]), record(metadata={'value': float('nan')}),
                   record(metadata={'value': float('inf')}), record(metadata={'value': 10**13}),
                   record(metadata={'value': list(range(17))}), record(metadata={'value': 'x' * 513}),
                   record(metadata={'a': {'b': {'c': {'d': 1}}}}), record(metadata={str(i): i for i in range(17)}),
                   record(metadata={'value': set()}), record(metadata={None: 'value'})]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.store.create(payload)
        self.assertEqual(len(self.store.list()), 1)
        with self.assertRaises(ValueError):
            self.store.reply(1, '🌿' * 501, True)

    def test_strict_identifiers_and_unknown_records(self):
        item = self.store.create(record())
        for identifier in (True, False, 0, -1, '1', 1.0, 2**63, 999):
            actions = (
                lambda: self.store.get(identifier),
                lambda: self.store.reply(identifier, 'Text', True),
                lambda: self.store.delete(identifier, True),
            )
            for action in actions:
                with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                    action()
        self.assertEqual(self.store.get(item['id'])['replies'], [])

    def test_concurrent_creates_cannot_exceed_the_record_limit(self):
        for number in range(MAX_RECORDS - 2):
            self.store.create(record(title='Existing ' + str(number)))

        def submit(number):
            try:
                return self.store.create(record(title='Concurrent ' + str(number)))['id']
            except ValueError:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            identifiers = list(pool.map(submit, range(8)))
        self.assertEqual(sum(identifier is not None for identifier in identifiers), 2)
        self.assertEqual(len(self.store.list()), MAX_RECORDS)

    def test_concurrent_reviews_award_a_quest_only_once(self):
        quest = self.store.create(record('quest', points=50, member_alias='a-reader'))
        self.store.transition(quest['id'], 'active', 'Start', True)
        self.store.transition(quest['id'], 'done', 'Complete', True)

        def review(_):
            try:
                self.store.transition(quest['id'], 'reviewed', 'Supplied review', True)
                return True
            except ValueError:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            successes = list(pool.map(review, range(8)))
        self.assertEqual(sum(successes), 1)
        self.assertEqual(self.store.leaderboard()['entries'][0]['points'], 50)
        self.assertEqual(len(self.store.get(quest['id'])['history']), 3)

    def test_shared_interaction_budget_blocks_each_kind_atomically(self):
        inquiry = self.store.create(record())
        survey = self.store.create(record('survey'))
        quest = self.store.create(record('quest'))
        for _ in range(MAX_INTERACTIONS - 2):
            self.store.reply(inquiry['id'], 'A supplied response.', True)
        self.store.vote(survey['id'], 0, True)
        self.store.transition(quest['id'], 'active', 'Start', True)
        actions = (
            lambda: self.store.reply(inquiry['id'], 'Overflow', True),
            lambda: self.store.vote(survey['id'], 1, True),
            lambda: self.store.transition(quest['id'], 'done', 'Overflow', True),
        )
        for action in actions:
            with self.assertRaises(ValueError):
                action()
        self.assertEqual(len(self.store.get(inquiry['id'])['replies']), MAX_INTERACTIONS - 2)
        self.assertEqual(self.store.get(survey['id'])['survey']['submissions'], 1)
        self.assertEqual(self.store.get(quest['id'])['state'], 'active')
        self.store.delete(survey['id'], True)
        self.store.transition(quest['id'], 'done', 'One slot was freed by deletion.', True)
        self.assertEqual(self.store.get(quest['id'])['state'], 'done')

    def test_database_symlink_is_rejected(self):
        link = Path(self.directory.name) / 'linked.sqlite3'
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            BoardStore(link)

    def test_database_ancestor_replacement_is_rejected_on_every_connection(self):
        base = Path(self.directory.name)
        state = base / 'state'
        store = BoardStore(state / 'boards.sqlite3')
        store.create(record())
        outside = base / 'outside'
        outside.mkdir()
        shutil.copyfile(store.path, outside / 'boards.sqlite3')
        before = (outside / 'boards.sqlite3').read_bytes()
        state.rename(base / 'previous-state')
        state.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            store.create(record())
        with self.assertRaises(ValueError):
            store.list()
        with self.assertRaises(ValueError):
            BoardStore(state / 'new.sqlite3')
        self.assertEqual((outside / 'boards.sqlite3').read_bytes(), before)
        self.assertFalse((outside / 'new.sqlite3').exists())

    def test_database_sidecar_symlinks_are_rejected_before_opening_sqlite(self):
        for suffix in ('-journal', '-wal', '-shm'):
            sidecar = Path(str(self.path) + suffix)
            sidecar.symlink_to(Path(self.directory.name) / 'outside')
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                self.store.create(record())
            sidecar.unlink()
        self.assertEqual(self.store.list(), [])


if __name__ == '__main__':
    unittest.main()
