import base64
import hashlib
import unittest

from madrigal_lab import media


class MediaTests(unittest.TestCase):
    def source(self, **changes):
        record = {'name': 'Owned notebook', 'encoding': 'utf8', 'data': 'A garden grows. A library opens.', 'owned': True, 'consent': True}
        record.update(changes)
        return record

    def story(self, **changes):
        record = {'title': 'Original story', 'book': 'one two three four five six seven eight nine ten eleven twelve', 'episodes': 2, 'scenes': 4, 'duration': 5, 'owned': True, 'consent': True}
        record.update(changes)
        return record

    def test_owned_utf8_digest_and_deterministic_seed(self):
        record = self.source(data='A café opens. 星星 shine.')
        first = media.raw_seed(record)
        self.assertEqual(first, media.raw_seed(record))
        self.assertEqual(first['source_sha256'], hashlib.sha256(record['data'].encode()).hexdigest())
        self.assertEqual(first['bytes'], len(record['data'].encode()))
        self.assertIn('星星', first['word_samples'])
        self.assertFalse(first['original_recoverable_from_seed'])
        self.assertFalse(first['server_retention'])

    def test_binary_round_trip_fingerprint_and_size_limit(self):
        raw = bytes(range(256)) * 256
        first = media.raw_seed(self.source(encoding='base64', data=base64.b64encode(raw).decode()))
        self.assertEqual(first['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(first['bytes'], 65536)
        self.assertEqual(first['word_samples'], [])
        for value in ('YWJj\n', 'YWJj=', '_notbase64', 'é', base64.b64encode(raw + b'a').decode()):
            with self.subTest(value=value[:20]), self.assertRaises(ValueError):
                media.raw_seed(self.source(encoding='base64', data=value))

    def test_input_boundary_and_assertions(self):
        for change in ({'owned': False}, {'owned': 1}, {'consent': 'true'}, {'data': ''}, {'data': 'é' * 32769}, {'encoding': 'memory'}, {'unknown': 1}, {'name': '\ud800'}):
            with self.subTest(change=str(change)[:50]), self.assertRaises(ValueError):
                media.raw_seed(self.source(**change))
        self.assertEqual(len(media.raw_seed(self.source(data='w ' * 50))['word_samples']), 32)

    def test_seed_rendition_bound_origin_and_finite_prompts(self):
        source = media.raw_seed(self.source())
        record = {key: source[key] for key in ('seed', 'source_sha256', 'source_name')}
        record.update(count=3, owned=True, consent=True)
        rendition = media.seed_rendition(record)
        self.assertEqual(rendition, media.seed_rendition(record))
        self.assertEqual(len(rendition['records']), 3)
        self.assertEqual(rendition['source_sha256'], source['source_sha256'])
        self.assertFalse(rendition['source_verified'])
        self.assertFalse(rendition['adaptation_of_original'])
        for changes in ({'count': True}, {'count': 33}, {'source_sha256': '0' * 64}, {'seed': '__import__("os")'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                media.seed_rendition(dict(record, **changes))

    def test_story_partition_covers_source_once_and_timed_cards(self):
        record = self.story(episodes=3, scenes=5, duration=7)
        plan = media.parse_story(record)
        self.assertEqual(plan, media.parse_story(record))
        scenes = [scene for episode in plan['episodes'] for scene in episode['scenes']]
        self.assertEqual(len(scenes), 5)
        self.assertEqual([scene['number'] for scene in scenes], [1, 2, 3, 4, 5])
        self.assertEqual(scenes[0]['source_word_range'][0], 0)
        self.assertEqual(scenes[-1]['source_word_range'][1], len(record['book'].split()))
        for left, right in zip(scenes, scenes[1:]):
            self.assertEqual(left['source_word_range'][1], right['source_word_range'][0])
        self.assertEqual(' '.join(scene['source_excerpt'] for scene in scenes), record['book'])
        self.assertEqual(plan['duration_seconds'], 35)
        self.assertFalse(plan['cinema_quality_verified'])
        self.assertFalse(plan['server_retention'])

    def test_story_limits_utf8_excerpt_and_plain_inert_text(self):
        for changes in ({'episodes': 9}, {'episodes': True}, {'scenes': 25}, {'episodes': 4, 'scenes': 3}, {'duration': 0}, {'duration': 31}, {'book': 'é' * 6001}, {'book': 'onlyword'}, {'consent': False}):
            with self.subTest(changes=str(changes)[:50]), self.assertRaises(ValueError):
                media.parse_story(self.story(**changes))
        plan = media.parse_story(self.story(book='<script>alert(1)</script> ' + '星星 ' * 1000, episodes=1, scenes=1))
        scene = plan['episodes'][0]['scenes'][0]
        self.assertIn('<script>', scene['source_excerpt'])
        self.assertLessEqual(len(scene['source_excerpt'].encode()), 640)
        self.assertTrue(scene['excerpt_truncated'])
        self.assertEqual(scene['shots'][0]['frame'], scene['source_excerpt'])


if __name__ == '__main__':
    unittest.main()
