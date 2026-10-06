"""Bounded obligations and documentary contracts for the DEMO_CREDIT ledger.

Nothing here contacts a bank, establishes a legal agreement, or authenticates a
person. Consent fields record what the local operator asserts.
"""
from contextlib import contextmanager
import hashlib
import json
import sqlite3
from pathlib import Path

from .finance import Ledger, name, units

MAX_RECORDS = 256
MAX_REPAYMENTS = 256


def _identifier(value):
    if type(value) is not int or not 1 <= value <= MAX_RECORDS:
        raise ValueError('Record ID must be an integer from 1 to 256')
    return value


def _label(value, limit=120):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError('Label must be nonempty text of at most %s characters without control characters' % limit)
    return value.strip()


def _body(value):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-8')) > 16384 or '\x00' in value:
        raise ValueError('Contract text must be nonempty UTF-8 text of at most 16384 bytes')
    return value


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


class Economy:
    """Use the existing ledger database, with atomic movements and finite records."""
    def __init__(self, ledger):
        if not isinstance(ledger, Ledger):
            raise ValueError('Economy requires a local demonstration Ledger')
        self.ledger = ledger
        with self.connection() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS economy_obligations(
                id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                lender TEXT NOT NULL REFERENCES accounts(name),
                borrower TEXT NOT NULL REFERENCES accounts(name),
                principal INTEGER NOT NULL CHECK(principal>0),
                paid INTEGER NOT NULL DEFAULT 0 CHECK(paid>=0 AND paid<=principal),
                state TEXT NOT NULL CHECK(state IN ('proposed','funded','settled')),
                funding_entry INTEGER REFERENCES entries(id), created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS economy_repayments(
                obligation INTEGER NOT NULL REFERENCES economy_obligations(id),
                entry INTEGER NOT NULL UNIQUE REFERENCES entries(id), amount INTEGER NOT NULL CHECK(amount>0));
            CREATE TABLE IF NOT EXISTS economy_coupons(
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
                kind TEXT NOT NULL CHECK(kind IN ('discount','subsidy')),
                state TEXT NOT NULL CHECK(state IN ('available','redeemed')),
                account TEXT REFERENCES accounts(name), created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS economy_contracts(
                id INTEGER PRIMARY KEY, version INTEGER NOT NULL, parent INTEGER REFERENCES economy_contracts(id),
                parent_sha256 TEXT, title TEXT NOT NULL, body TEXT NOT NULL, content_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('proposed','reviewed','finalised')),
                reviewer TEXT, review_asserted INTEGER NOT NULL DEFAULT 0,
                author TEXT, consent_asserted INTEGER NOT NULL DEFAULT 0,
                receipt_payload TEXT, receipt_sha256 TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
            ''')

    def _boundary(self):
        path = Path(self.ledger.path).absolute()
        for candidate in (path, *path.parents):
            if candidate.is_symlink():
                raise ValueError('Demo database and its parents must not be symlinks')
        if not path.is_file():
            raise ValueError('Demo database must be a regular local file')
        for suffix in ('-journal', '-wal', '-shm'):
            if Path(str(path) + suffix).is_symlink():
                raise ValueError('Demo database sidecars must not be symlinks')

    @contextmanager
    def connection(self):
        self._boundary()
        with self.ledger.connection() as db:
            db.row_factory = sqlite3.Row
            yield db

    @staticmethod
    def _limit(db, table):
        if db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] >= MAX_RECORDS:
            raise ValueError('This demonstration allows at most 256 records per collection')

    @staticmethod
    def _accounts(db, src, dst=None):
        for value in (src,) if dst is None else (src, dst):
            name(value)
            if not db.execute('SELECT 1 FROM accounts WHERE name=?', (value,)).fetchone():
                raise ValueError('Unknown account: ' + value)
        if dst is not None and src == dst:
            raise ValueError('Choose different accounts')

    @staticmethod
    def _post(db, src, dst, amount, kind):
        """Internal transfer in the caller's transaction; never creates units."""
        Economy._accounts(db, src, dst)
        amount = units(amount)
        balance = db.execute('SELECT COALESCE(SUM(delta),0) FROM postings WHERE account=?', (src,)).fetchone()[0]
        if balance < amount:
            raise ValueError('Insufficient demo balance')
        entry = db.execute('INSERT INTO entries(kind,src,dst,amount) VALUES(?,?,?,?)', (kind, src, dst, amount)).lastrowid
        db.executemany('INSERT INTO postings VALUES(?,?,?)', [(entry, src, -amount), (entry, dst, amount)])
        return entry

    @staticmethod
    def _obligation(db, value):
        row = db.execute('SELECT * FROM economy_obligations WHERE id=?', (_identifier(value),)).fetchone()
        if row is None:
            raise ValueError('Unknown obligation')
        result = dict(row)
        result['outstanding'] = result['principal'] - result['paid'] if result['state'] != 'proposed' else 0
        result['currency'] = 'DEMO_CREDIT'
        result['simulated'] = True
        return result

    def create_obligation(self, lender, borrower, amount, title='Demo obligation'):
        amount, title = units(amount), _label(title)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._accounts(db, lender, borrower)
            self._limit(db, 'economy_obligations')
            value = db.execute('INSERT INTO economy_obligations(title,lender,borrower,principal,state) VALUES(?,?,?,?,?)',
                               (title, lender, borrower, amount, 'proposed')).lastrowid
            return self._obligation(db, value)

    def lend(self, obligation_id):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            record = self._obligation(db, obligation_id)
            if record['state'] != 'proposed':
                raise ValueError('Only a proposed obligation can be funded')
            entry = self._post(db, record['lender'], record['borrower'], record['principal'], 'demo-loan')
            db.execute("UPDATE economy_obligations SET state='funded',funding_entry=? WHERE id=?", (entry, obligation_id))
            return self._obligation(db, obligation_id)

    def repay(self, obligation_id, amount):
        amount = units(amount)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            record = self._obligation(db, obligation_id)
            if record['state'] != 'funded' or amount > record['outstanding']:
                raise ValueError('Repayment requires a funded obligation and cannot exceed outstanding units')
            count = db.execute('SELECT COUNT(*) FROM economy_repayments WHERE obligation=?', (obligation_id,)).fetchone()[0]
            if count >= MAX_REPAYMENTS:
                raise ValueError('An obligation allows at most 256 repayment records')
            if count == MAX_REPAYMENTS - 1 and amount != record['outstanding']:
                raise ValueError('The final repayment record must settle the full outstanding amount')
            entry = self._post(db, record['borrower'], record['lender'], amount, 'demo-repayment')
            paid = record['paid'] + amount
            db.execute('INSERT INTO economy_repayments VALUES(?,?,?)', (obligation_id, entry, amount))
            db.execute('UPDATE economy_obligations SET paid=?,state=? WHERE id=?',
                       (paid, 'settled' if paid == record['principal'] else 'funded', obligation_id))
            return self._obligation(db, obligation_id)

    def create_coupon(self, title, amount, kind='discount'):
        title, amount = _label(title), units(amount)
        if kind not in ('discount', 'subsidy'):
            raise ValueError('Coupon kind must be discount or subsidy')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._limit(db, 'economy_coupons')
            value = db.execute("INSERT INTO economy_coupons(title,amount,kind,state) VALUES(?,?,?,'available')", (title, amount, kind)).lastrowid
            return self._coupon(db, value)

    @staticmethod
    def _coupon(db, value):
        row = db.execute('SELECT * FROM economy_coupons WHERE id=?', (_identifier(value),)).fetchone()
        if row is None:
            raise ValueError('Unknown coupon')
        result = dict(row)
        result.update(currency='DEMO_CREDIT', simulated=True, transfers_units=False)
        return result

    def redeem_coupon(self, coupon_id, account):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._accounts(db, account)
            record = self._coupon(db, coupon_id)
            if record['state'] != 'available':
                raise ValueError('Coupon has already been redeemed')
            db.execute("UPDATE economy_coupons SET state='redeemed',account=? WHERE id=?", (account, coupon_id))
            return self._coupon(db, coupon_id)

    @staticmethod
    def _contract(db, value, include_body=True):
        row = db.execute('SELECT * FROM economy_contracts WHERE id=?', (_identifier(value),)).fetchone()
        if row is None:
            raise ValueError('Unknown contract')
        result = dict(row)
        result.update(simulated=True, legally_binding=False, consent_verified=False)
        if not include_body:
            result.pop('body')
            result.pop('receipt_payload')
        return result

    @staticmethod
    def _content(record):
        return {key: record[key] for key in ('id', 'version', 'parent', 'parent_sha256', 'title', 'body')}

    def _verify(self, db, record, seen=None):
        seen = set() if seen is None else seen
        if record['id'] in seen or len(seen) >= MAX_RECORDS:
            return False
        seen.add(record['id'])
        if _digest(self._content(record)) != record['content_sha256']:
            return False
        if record['state'] == 'proposed' and (record['reviewer'] is not None or record['review_asserted'] != 0):
            return False
        if record['state'] in ('reviewed', 'finalised') and (not record['reviewer'] or record['review_asserted'] != 1):
            return False
        if record['state'] != 'finalised' and any(record[key] is not None for key in ('author', 'receipt_payload', 'receipt_sha256')):
            return False
        if record['state'] != 'finalised' and record['consent_asserted'] != 0:
            return False
        if record['parent'] is not None:
            parent = self._contract(db, record['parent'])
            if parent['state'] != 'finalised' or parent['content_sha256'] != record['parent_sha256'] or parent['version'] + 1 != record['version']:
                return False
            if not self._verify(db, parent, seen):
                return False
        elif record['version'] != 1 or record['parent_sha256'] is not None:
            return False
        if record['state'] == 'finalised':
            try:
                payload = json.loads(record['receipt_payload'])
            except (TypeError, ValueError):
                return False
            expected = {key: record[key] for key in ('id', 'version', 'parent', 'content_sha256', 'reviewer', 'review_asserted', 'author', 'consent_asserted')}
            if payload != expected or _digest(payload) != record['receipt_sha256'] or record['review_asserted'] != 1 or record['consent_asserted'] != 1:
                return False
        return True

    def create_contract(self, title, text, parent_id=None):
        title, text = _label(title), _body(text)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._limit(db, 'economy_contracts')
            version, parent_hash = 1, None
            if parent_id is not None:
                parent = self._contract(db, parent_id)
                if parent['state'] != 'finalised' or not self._verify(db, parent):
                    raise ValueError('A new version requires an intact finalised parent')
                version, parent_hash = parent['version'] + 1, parent['content_sha256']
            value = db.execute("INSERT INTO economy_contracts(version,parent,parent_sha256,title,body,content_sha256,state) VALUES(?,?,?,?,?,'','proposed')",
                               (version, parent_id, parent_hash, title, text)).lastrowid
            record = self._contract(db, value)
            db.execute('UPDATE economy_contracts SET content_sha256=? WHERE id=?', (_digest(self._content(record)), value))
            return self._contract(db, value)

    def review_contract(self, contract_id, reviewer, consent_asserted=False):
        reviewer = _label(reviewer, 80)
        if consent_asserted is not True:
            raise ValueError('Review requires an explicit local consent assertion')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            record = self._contract(db, contract_id)
            if record['state'] != 'proposed' or not self._verify(db, record):
                raise ValueError('Review requires an intact proposed contract')
            db.execute("UPDATE economy_contracts SET state='reviewed',reviewer=?,review_asserted=1 WHERE id=?", (reviewer, contract_id))
            return self._contract(db, contract_id)

    def finalise_contract(self, contract_id, author, consent_asserted=False):
        author = _label(author, 80)
        if consent_asserted is not True:
            raise ValueError('Finalisation requires an explicit local consent assertion')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            record = self._contract(db, contract_id)
            if record['state'] != 'reviewed' or record['review_asserted'] != 1 or not self._verify(db, record):
                raise ValueError('Finalisation requires an intact reviewed contract')
            record.update(author=author, consent_asserted=1)
            payload = {key: record[key] for key in ('id', 'version', 'parent', 'content_sha256', 'reviewer', 'review_asserted', 'author', 'consent_asserted')}
            db.execute("UPDATE economy_contracts SET state='finalised',author=?,consent_asserted=1,receipt_payload=?,receipt_sha256=? WHERE id=?",
                       (author, json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')), _digest(payload), contract_id))
            return self._contract(db, contract_id)

    def verify_contract(self, contract_id):
        with self.connection() as db:
            record = self._contract(db, contract_id)
            return {'id': record['id'], 'version': record['version'], 'state': record['state'], 'intact': self._verify(db, record),
                    'content_sha256': record['content_sha256'], 'receipt_sha256': record['receipt_sha256'],
                    'authenticates_person': False, 'legally_binding': False,
                    'scope': 'Local SHA-256 content and revision consistency; no external identity verification'}

    def report(self):
        """One transaction gives a consistent portfolio and obligation reconciliation."""
        with self.connection() as db:
            db.execute('BEGIN')
            for table in ('economy_obligations', 'economy_coupons', 'economy_contracts'):
                if db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] > MAX_RECORDS:
                    raise ValueError('Stored demonstration collection exceeds 256 records')
            if db.execute('SELECT COUNT(*) FROM economy_repayments').fetchone()[0] > MAX_RECORDS * MAX_REPAYMENTS or db.execute(
                    'SELECT obligation FROM economy_repayments GROUP BY obligation HAVING COUNT(*)>? LIMIT 1', (MAX_REPAYMENTS,)).fetchone():
                raise ValueError('Stored demonstration repayment collection exceeds its finite budget')
            balances = dict(db.execute('SELECT a.name,COALESCE(SUM(p.delta),0) FROM accounts a LEFT JOIN postings p ON a.name=p.account GROUP BY a.name ORDER BY a.name').fetchall())
            obligations = [self._obligation(db, row[0]) for row in db.execute('SELECT id FROM economy_obligations ORDER BY id LIMIT 256').fetchall()]
            coupons = [self._coupon(db, row[0]) for row in db.execute('SELECT id FROM economy_coupons ORDER BY id LIMIT 256').fetchall()]
            full_contracts = [self._contract(db, row[0]) for row in db.execute('SELECT id FROM economy_contracts ORDER BY id LIMIT 256').fetchall()]
            contracts = []
            for record in full_contracts:
                item = {key: value for key, value in record.items() if key not in ('body', 'receipt_payload')}
                item['intact'] = self._verify(db, record)
                contracts.append(item)
            unbalanced = db.execute('SELECT entry FROM postings GROUP BY entry HAVING SUM(delta)<>0').fetchall()
            invalid_entries = db.execute('''SELECT e.id FROM entries e LEFT JOIN postings p ON p.entry=e.id GROUP BY e.id
                HAVING COUNT(p.entry)<>2 OR SUM(CASE WHEN p.account=e.src AND p.delta=-e.amount THEN 1 ELSE 0 END)<>1
                OR SUM(CASE WHEN p.account=e.dst AND p.delta=e.amount THEN 1 ELSE 0 END)<>1''').fetchall()
            reconciliation = True
            for item in obligations:
                repayments = db.execute('''SELECT r.amount,e.kind,e.src,e.dst,e.amount FROM economy_repayments r
                    LEFT JOIN entries e ON e.id=r.entry WHERE r.obligation=?''', (item['id'],)).fetchall()
                if item['state'] == 'proposed':
                    if item['paid'] != 0 or item['funding_entry'] is not None or repayments:
                        reconciliation = False
                    continue
                funding = db.execute('SELECT kind,src,dst,amount FROM entries WHERE id=?', (item['funding_entry'],)).fetchone()
                paid = sum(row[0] for row in repayments)
                matched = all(tuple(row[1:]) == ('demo-repayment', item['borrower'], item['lender'], row[0]) for row in repayments)
                if funding is None or tuple(funding) != ('demo-loan', item['lender'], item['borrower'], item['principal']) or not matched or paid != item['paid'] or (item['state'] == 'settled') != (item['paid'] == item['principal']):
                    reconciliation = False
            portfolio = []
            for account, balance in balances.items():
                if account == 'issuer':
                    continue
                receivable = sum(item['outstanding'] for item in obligations if item['lender'] == account)
                payable = sum(item['outstanding'] for item in obligations if item['borrower'] == account)
                portfolio.append({'account': account, 'balance': balance, 'receivable': receivable, 'payable': payable,
                                  'demo_net_position': balance + receivable - payable})
            minted = db.execute("SELECT COALESCE(SUM(amount),0) FROM entries WHERE kind='mint'").fetchone()[0]
        return {'currency': 'DEMO_CREDIT', 'simulated': True, 'accounts': balances, 'total_minted': minted,
                'obligations': obligations, 'coupons': coupons, 'contracts': contracts, 'portfolio': portfolio,
                'audit': {'balanced': sum(balances.values()) == 0 and not unbalanced and not invalid_entries,
                          'obligations_reconciled': reconciliation, 'contracts_intact': all(c['intact'] for c in contracts),
                          'independent_audit': False},
                'scope': 'Local hypothetical accounting and document consistency, without real payments or binding contracts'}
