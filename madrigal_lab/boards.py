"""Finite, local community records, surveys and fictional quest workflows.

Consent and aliases are supplied assertions. This store neither authenticates
people nor publishes messages, and quest points never represent money.
"""
from contextlib import contextmanager
import json
import math
from pathlib import Path
import sqlite3


KINDS = (
    'advice', 'guidance', 'manual', 'inquiry', 'survey', 'quest', 'logistics',
    'fandom', 'community', 'media', 'learning', 'preferences', 'map', 'radio',
    'diary', 'contract', 'recipe', 'genealogy', 'research', 'health', 'record',
)
MAX_RECORDS = 256
MAX_DEPTH = 8
MAX_INTERACTIONS = 1024
MAX_POINTS = 1000
QUEST_TRANSITIONS = {
    'open': {'active', 'cancelled'},
    'active': {'done', 'cancelled'},
    'done': {'active', 'reviewed', 'cancelled'},
    'reviewed': set(),
    'cancelled': set(),
}


def _consent(value):
    if value is not True:
        raise ValueError('Explicit consent must be the Boolean true before saving a local record')


def _text(value, maximum, field, required=True):
    if not isinstance(value, str):
        raise ValueError(field + ' must be text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeEncodeError as error:
        raise ValueError(field + ' must be valid UTF-8 text') from error
    if size > maximum or (required and not value.strip()) or '\x00' in value:
        raise ValueError(field + ' must be nonempty, bounded UTF-8 text without NUL')
    return value


def _integer(value, minimum, maximum, field):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(field + ' must be an integer within its declared range')
    return value


def _identifier(value):
    return _integer(value, 1, 2**63 - 1, 'Record identifier')


def _metadata(value):
    """Validate bounded JSON rather than accepting arbitrary Python objects."""
    if type(value) is not dict:
        raise ValueError('Metadata must be a JSON object')
    count = 0

    def visit(item, depth):
        nonlocal count
        count += 1
        if count > 128 or depth > 3:
            raise ValueError('Metadata is limited to 128 values and three nested levels')
        if type(item) is dict:
            if len(item) > 16:
                raise ValueError('Metadata objects are limited to 16 fields')
            for key, child in item.items():
                _text(key, 80, 'Metadata key')
                visit(child, depth + 1)
        elif type(item) is list:
            if len(item) > 16:
                raise ValueError('Metadata lists are limited to 16 values')
            for child in item:
                visit(child, depth + 1)
        elif isinstance(item, str):
            _text(item, 512, 'Metadata text', required=False)
        elif item is None or type(item) is bool:
            pass
        elif type(item) is int:
            if abs(item) > 10**12:
                raise ValueError('Metadata integer exceeds the declared range')
        elif type(item) is float:
            if not math.isfinite(item) or abs(item) > 10**12:
                raise ValueError('Metadata numbers must be finite and bounded')
        else:
            raise ValueError('Metadata supports JSON values only')

    visit(value, 0)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if len(encoded.encode('utf-8')) > 8192:
        raise ValueError('Metadata exceeds 8 KiB')
    return encoded


class BoardStore:
    """An SQLite record tree with atomic limits and no remote side effects."""

    def __init__(self, path):
        self.path = Path(path)
        self._boundary()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS board_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    parent INTEGER REFERENCES board_records(id) ON DELETE RESTRICT,
                    metadata TEXT NOT NULL,
                    member_alias TEXT NOT NULL,
                    options TEXT,
                    points INTEGER,
                    state TEXT,
                    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS board_parent ON board_records(parent);
                CREATE TABLE IF NOT EXISTS board_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record INTEGER NOT NULL REFERENCES board_records(id) ON DELETE CASCADE,
                    body TEXT NOT NULL,
                    member_alias TEXT NOT NULL,
                    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS board_votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record INTEGER NOT NULL REFERENCES board_records(id) ON DELETE CASCADE,
                    option_index INTEGER NOT NULL,
                    member_alias TEXT NOT NULL,
                    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS board_transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record INTEGER NOT NULL REFERENCES board_records(id) ON DELETE CASCADE,
                    state TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            ''')

    def _boundary(self):
        path = self.path.absolute()
        if any(candidate.is_symlink() for candidate in (path, *path.parents)):
            raise ValueError('The board database and its parents must not be symlinks')
        if path.exists() and not path.is_file():
            raise ValueError('The board database must be a regular local file')
        if any(Path(str(path) + suffix).is_symlink() for suffix in ('-journal', '-wal', '-shm')):
            raise ValueError('Board database sidecars must not be symlinks')

    @contextmanager
    def connection(self):
        self._boundary()
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _lookup(db, identifier):
        row = db.execute('SELECT * FROM board_records WHERE id=?', (identifier,)).fetchone()
        if row is None:
            raise ValueError('Unknown local board record')
        return row

    @staticmethod
    def _record(row):
        result = {key: row[key] for key in ('id', 'kind', 'title', 'body', 'parent', 'member_alias', 'created')}
        result['metadata'] = json.loads(row['metadata'])
        result['consent_reported'] = True
        if row['kind'] == 'survey':
            result['options'] = json.loads(row['options'])
        if row['kind'] == 'quest':
            result.update(points=row['points'], state=row['state'], point_unit='FICTIONAL_QUEST_POINT')
        if row['kind'] == 'health':
            result['scope'] = 'Supplied personal record; no diagnosis or health inference'
        return result

    @staticmethod
    def _interaction_limit(db):
        total = sum(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
                    for table in ('board_replies', 'board_votes', 'board_transitions'))
        if total >= MAX_INTERACTIONS:
            raise ValueError('The local reply, vote and quest-history budget is full')

    def create(self, record):
        if type(record) is not dict:
            raise ValueError('Supply a board record object')
        allowed = {'kind', 'title', 'body', 'parent', 'metadata', 'member_alias', 'options', 'points', 'consent'}
        if set(record) - allowed:
            raise ValueError('Unknown board record fields')
        _consent(record.get('consent'))
        kind = record.get('kind')
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError('Choose a declared local board kind')
        title = _text(record.get('title'), 160, 'Title')
        body = _text(record.get('body'), 8000, 'Body')
        alias = _text(record.get('member_alias', 'anonymous'), 80, 'Supplied member alias')
        metadata = _metadata(record.get('metadata', {}))
        parent = record.get('parent')
        if parent is not None:
            _identifier(parent)
        options = None
        if kind == 'survey':
            supplied = record.get('options')
            if type(supplied) is not list or not 2 <= len(supplied) <= 8:
                raise ValueError('A survey needs two to eight options')
            options = [_text(value, 160, 'Survey option') for value in supplied]
            if len({option.strip().casefold() for option in options}) != len(options):
                raise ValueError('Survey options must be distinct')
        elif 'options' in record:
            raise ValueError('Options are available only for surveys')
        points = None
        if kind == 'quest':
            points = _integer(record.get('points', 0), 0, MAX_POINTS, 'Fictional quest points')
        elif 'points' in record:
            raise ValueError('Points are available only for fictional quests')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT COUNT(*) FROM board_records').fetchone()[0] >= MAX_RECORDS:
                raise ValueError('The local board is limited to 256 records')
            depth = 1
            cursor = parent
            while cursor is not None:
                row = self._lookup(db, cursor)
                depth += 1
                if depth > MAX_DEPTH:
                    raise ValueError('The local board tree is limited to eight levels')
                cursor = row['parent']
            identifier = db.execute('''INSERT INTO board_records
                (kind,title,body,parent,metadata,member_alias,options,points,state)
                VALUES(?,?,?,?,?,?,?,?,?)''', (
                    kind, title, body, parent, metadata, alias,
                    json.dumps(options, ensure_ascii=False) if options is not None else None,
                    points, 'open' if kind == 'quest' else None)).lastrowid
            result = self._record(self._lookup(db, identifier))
        return result

    def list(self, kind=None):
        if kind is not None and (not isinstance(kind, str) or kind not in KINDS):
            raise ValueError('Choose a declared local board kind')
        with self.connection() as db:
            if kind is None:
                rows = db.execute('SELECT * FROM board_records ORDER BY id').fetchall()
            else:
                rows = db.execute('SELECT * FROM board_records WHERE kind=? ORDER BY id', (kind,)).fetchall()
            return [self._record(row) for row in rows]

    def get(self, identifier):
        _identifier(identifier)
        with self.connection() as db:
            db.execute('BEGIN')
            row = self._lookup(db, identifier)
            result = self._record(row)
            result['replies'] = [dict(reply) for reply in db.execute(
                'SELECT id,body,member_alias,created FROM board_replies WHERE record=? ORDER BY id', (identifier,))]
            if row['kind'] == 'survey':
                totals = dict(db.execute('SELECT option_index,COUNT(*) FROM board_votes WHERE record=? GROUP BY option_index', (identifier,)))
                result['survey'] = {
                    'options': [{'index': index, 'label': label, 'votes': totals.get(index, 0)}
                                for index, label in enumerate(result['options'])],
                    'submissions': sum(totals.values()),
                    'verified_participants': False,
                    'scope': 'Local submissions; repeated submissions are possible without authentication',
                }
            if row['kind'] == 'quest':
                result['history'] = [dict(event) for event in db.execute(
                    'SELECT id,state,reason,created FROM board_transitions WHERE record=? ORDER BY id', (identifier,))]
            return result

    def tree(self, parent=None, depth=MAX_DEPTH, limit=MAX_RECORDS):
        if parent is not None:
            _identifier(parent)
        _integer(depth, 1, MAX_DEPTH, 'Tree display depth')
        _integer(limit, 1, MAX_RECORDS, 'Tree display record limit')
        with self.connection() as db:
            rows = db.execute('SELECT * FROM board_records ORDER BY id').fetchall()
        records = {row['id']: self._record(row) for row in rows}
        children = {}
        for record in records.values():
            children.setdefault(record['parent'], []).append(record['id'])
        if parent is not None and parent not in records:
            raise ValueError('Unknown local board record')

        visited = set()
        truncated = False

        def branch(identifier, level):
            nonlocal truncated
            if identifier in visited:
                raise ValueError('The stored board tree contains a cycle')
            visited.add(identifier)
            result = records[identifier]
            result['children'] = []
            for child in children.get(identifier, []):
                if level >= depth or len(visited) >= limit:
                    truncated = True
                    break
                result['children'].append(branch(child, level + 1))
            return result

        roots = []
        for identifier in ([parent] if parent is not None else children.get(None, [])):
            if len(visited) >= limit:
                truncated = True
                break
            roots.append(branch(identifier, 1))
        return {'roots': roots, 'records': len(records), 'returned_records': len(visited),
                'depth_limit': MAX_DEPTH, 'display_depth': depth, 'display_limit': limit,
                'truncated': truncated,
                'scope': 'Finite local record tree; records are inert supplied text'}

    def delete(self, identifier, consent):
        _identifier(identifier)
        _consent(consent)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._lookup(db, identifier)
            if db.execute('SELECT 1 FROM board_records WHERE parent=?', (identifier,)).fetchone():
                raise ValueError('Delete child records before deleting their parent')
            replies = db.execute('SELECT COUNT(*) FROM board_replies WHERE record=?', (identifier,)).fetchone()[0]
            votes = db.execute('SELECT COUNT(*) FROM board_votes WHERE record=?', (identifier,)).fetchone()[0]
            db.execute('DELETE FROM board_records WHERE id=?', (identifier,))
        return {'deleted': identifier, 'deleted_replies': replies, 'deleted_votes': votes}

    def reply(self, identifier, body, consent, member_alias='anonymous'):
        _identifier(identifier)
        _consent(consent)
        body = _text(body, 2000, 'Reply')
        alias = _text(member_alias, 80, 'Supplied member alias')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._lookup(db, identifier)
            self._interaction_limit(db)
            reply_id = db.execute('INSERT INTO board_replies(record,body,member_alias) VALUES(?,?,?)',
                                  (identifier, body, alias)).lastrowid
            result = dict(db.execute('SELECT id,record,body,member_alias,created FROM board_replies WHERE id=?', (reply_id,)).fetchone())
        return result

    def vote(self, identifier, option, consent, member_alias='anonymous'):
        _identifier(identifier)
        _consent(consent)
        _integer(option, 0, 7, 'Survey option index')
        alias = _text(member_alias, 80, 'Supplied member alias')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._lookup(db, identifier)
            if row['kind'] != 'survey' or option >= len(json.loads(row['options'])):
                raise ValueError('Choose an existing option of a survey record')
            self._interaction_limit(db)
            vote_id = db.execute('INSERT INTO board_votes(record,option_index,member_alias) VALUES(?,?,?)',
                                 (identifier, option, alias)).lastrowid
        return {'id': vote_id, 'record': identifier, 'option': option,
                'member_alias': alias, 'verified_participant': False}

    def transition(self, identifier, state, reason, consent):
        _identifier(identifier)
        _consent(consent)
        if not isinstance(state, str) or state not in QUEST_TRANSITIONS:
            raise ValueError('Choose a declared fictional quest state')
        reason = _text(reason, 1000, 'Quest transition reason')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._lookup(db, identifier)
            if row['kind'] != 'quest' or state not in QUEST_TRANSITIONS[row['state']]:
                raise ValueError('Invalid fictional quest transition')
            self._interaction_limit(db)
            db.execute('UPDATE board_records SET state=? WHERE id=?', (state, identifier))
            db.execute('INSERT INTO board_transitions(record,state,reason) VALUES(?,?,?)', (identifier, state, reason))
            result = self._record(self._lookup(db, identifier))
        result['review_verified'] = False
        return result

    def leaderboard(self):
        with self.connection() as db:
            rows = db.execute('''SELECT member_alias,SUM(points) AS points,COUNT(*) AS reviewed_quests
                FROM board_records WHERE kind='quest' AND state='reviewed'
                GROUP BY member_alias ORDER BY points DESC,member_alias ASC''').fetchall()
        return {'entries': [dict(row) for row in rows], 'unit': 'FICTIONAL_QUEST_POINT',
                'verified_review': False, 'financial_value': False,
                'scope': 'Supplied points on locally reviewed fictional quests, grouped by supplied aliases; no ranking of people'}
