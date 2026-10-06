"""Bounded, deterministic transformations of deliberately supplied owned material.

This module does not read files, memory, devices, accounts or network resources.
Ownership and participant consent are user assertions, not verified permissions.
"""
import base64
import binascii
import hashlib
import re

from . import papers

MAX_RAW_BYTES = 65536
MAX_BOOK_BYTES = 12000


def _record(record, fields):
    if not isinstance(record, dict) or set(record) - fields:
        raise ValueError('Supply only the declared media fields')
    if record.get('owned') is not True or record.get('consent') is not True:
        raise ValueError('Confirm rights to the supplied material and participant consent')


def _text(value, maximum, label, required=True):
    if not isinstance(value, str):
        raise ValueError(label + ' must be text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError as error:
        raise ValueError(label + ' must be valid UTF-8') from error
    if size > maximum or (required and not value.strip()):
        raise ValueError(label + ' is empty or exceeds its UTF-8 byte limit')
    return value


def _integer(value, lower, upper, label):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f'{label} must be an integer in {lower}..{upper}')
    return value


def _prefix(text, maximum):
    return text.encode('utf-8')[:maximum].decode('utf-8', errors='ignore')


def raw_seed(record):
    """Describe up to 64 KiB of supplied data and derive a content-addressed seed.

    A seed identifies the bytes; it cannot reconstruct them. Keep the original
    file or a verified owner-controlled backup when recovery is required.
    """
    _record(record, {'name', 'encoding', 'data', 'owned', 'consent'})
    name = _text(record.get('name'), 160, 'Source name')
    encoding = record.get('encoding', 'utf8')
    if encoding == 'utf8':
        original = _text(record.get('data'), MAX_RAW_BYTES, 'Raw data')
        raw = original.encode('utf-8')
        samples = [_prefix(word, 80) for word in original.split()[:32]]
    elif encoding == 'base64':
        encoded = _text(record.get('data'), 87384, 'Base64 data')
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError('Use canonical ASCII base64 without whitespace') from error
        if not raw or len(raw) > MAX_RAW_BYTES or base64.b64encode(raw).decode('ascii') != encoded:
            raise ValueError('Use canonical base64 encoding of 1..65536 bytes')
        samples = []
    else:
        raise ValueError('Encoding must be utf8 or base64')
    digest = hashlib.sha256(raw).hexdigest()
    return {
        'source_name': name, 'source_encoding': encoding,
        'source_sha256': digest, 'bytes': len(raw),
        'seed': 'rasniki-data-seed:' + digest, 'word_samples': samples,
        'ownership_asserted': True, 'consent_asserted': True,
        'server_retention': False, 'original_recoverable_from_seed': False,
        'scope': 'Content fingerprint and original-fiction seed; no memory or disk recovery.',
    }


def seed_rendition(record):
    """Produce original finite prompts with a supplied source reference attached."""
    _record(record, {'seed', 'source_sha256', 'source_name', 'count', 'owned', 'consent'})
    seed = _text(record.get('seed'), 512, 'Seed')
    name = _text(record.get('source_name'), 160, 'Source name')
    digest = record.get('source_sha256')
    if not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
        raise ValueError('Source digest must be a lowercase SHA-256 hexadecimal value')
    if seed != 'rasniki-data-seed:' + digest:
        raise ValueError('Seed must match the supplied source digest')
    count = _integer(record.get('count', 4), 1, 32, 'Count')
    result = papers.fandom(seed, count)
    result.update({
        'source_name': name, 'source_sha256': digest,
        'source_verified': False, 'adaptation_of_original': False,
        'ownership_asserted': True, 'consent_asserted': True,
        'server_retention': False,
        'scope': 'Original fictional prompts derived from a supplied fingerprint; the source bytes are not reconstructed or interpreted.',
    })
    return result


def parse_story(record):
    """Partition supplied book text into an editable finite production plan.

    This deterministic text splitter does not understand narrative continuity or
    generate film footage. Its excerpt cards can support a local timed animatic.
    """
    _record(record, {'title', 'book', 'episodes', 'scenes', 'duration', 'owned', 'consent'})
    title = _text(record.get('title'), 160, 'Title')
    book = _text(record.get('book'), MAX_BOOK_BYTES, 'Book specification')
    episodes = _integer(record.get('episodes', 1), 1, 8, 'Episodes')
    scenes = _integer(record.get('scenes', 4), 1, 24, 'Total scenes')
    duration = _integer(record.get('duration', 5), 1, 30, 'Shot duration in seconds')
    if episodes > scenes:
        raise ValueError('Each episode needs at least one scene')
    words = book.split()
    if len(words) < scenes:
        raise ValueError('Supply at least one word for each requested scene')
    episode_list = []
    scene_index = 0
    for episode_index in range(episodes):
        first_scene = episode_index * scenes // episodes
        last_scene = (episode_index + 1) * scenes // episodes
        scene_list = []
        for _ in range(first_scene, last_scene):
            start = scene_index * len(words) // scenes
            end = (scene_index + 1) * len(words) // scenes
            passage = ' '.join(words[start:end])
            excerpt = _prefix(passage, 640)
            scene_list.append({
                'number': scene_index + 1,
                'title': f'Scene {scene_index + 1}',
                'source_word_range': [start, end],
                'source_excerpt': excerpt,
                'excerpt_truncated': excerpt != passage,
                'shots': [{
                    'number': 1, 'duration_seconds': duration,
                    'frame': excerpt, 'camera': 'Text card; editable storyboard placeholder',
                    'audio': 'No generated audio; add a permitted local soundtrack separately.',
                }],
            })
            scene_index += 1
        episode_list.append({'number': episode_index + 1, 'title': f'Episode {episode_index + 1}', 'scenes': scene_list})
    return {
        'title': title, 'source_sha256': hashlib.sha256(book.encode('utf-8')).hexdigest(),
        'source_bytes': len(book.encode('utf-8')), 'episodes': episode_list,
        'episode_count': episodes, 'scene_count': scenes, 'shot_count': scenes,
        'duration_seconds': scenes * duration,
        'format': 'local-text-card-production-plan',
        'ownership_asserted': True, 'consent_asserted': True,
        'server_retention': False, 'cinema_quality_verified': False,
        'scope': 'Deterministic book excerpts and timed animatic cards; human editing, casting, filming and rights review are still required.',
    }
