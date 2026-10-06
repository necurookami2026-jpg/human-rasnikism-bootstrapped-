"""Persistent double-entry demonstration ledger; no money or banking connection."""
import re
from contextlib import contextmanager
import sqlite3
from pathlib import Path

MAX_UNITS = 10**12


def units(value):
    if type(value) is not int or not 1 <= value <= MAX_UNITS:
        raise ValueError('Amount must be 1..1000000000000 integer DEMO_CREDIT units')
    return value


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,39}', value) or value == 'issuer':
        raise ValueError('Account needs a letter-led name of up to 40 characters; issuer is reserved')
    return value


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS accounts(name TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, src TEXT NOT NULL, dst TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0), created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS postings(entry INTEGER NOT NULL REFERENCES entries(id), account TEXT NOT NULL REFERENCES accounts(name), delta INTEGER NOT NULL);
            INSERT OR IGNORE INTO accounts VALUES('issuer');''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def account(self, value):
        value = name(value)
        with self.connection() as db:
            db.execute('INSERT OR IGNORE INTO accounts VALUES(?)', (value,))
        return {'account': value, 'currency': 'DEMO_CREDIT'}

    def post(self, src, dst, amount, kind):
        amount = units(amount)
        name(dst)
        if src != 'issuer':
            name(src)
        if src == dst:
            raise ValueError('Choose different accounts')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            for account in (src, dst):
                if not db.execute('SELECT 1 FROM accounts WHERE name=?', (account,)).fetchone():
                    raise ValueError('Unknown account: ' + account)
            balance = db.execute('SELECT COALESCE(SUM(delta),0) FROM postings WHERE account=?', (src,)).fetchone()[0]
            if src != 'issuer' and balance < amount:
                raise ValueError('Insufficient demo balance')
            if kind == 'mint':
                issued = db.execute("SELECT COALESCE(SUM(amount),0) FROM entries WHERE kind='mint'").fetchone()[0]
                if issued + amount > MAX_UNITS:
                    raise ValueError('Demo issuance limit reached')
            entry = db.execute('INSERT INTO entries(kind,src,dst,amount) VALUES(?,?,?,?)', (kind, src, dst, amount)).lastrowid
            db.executemany('INSERT INTO postings VALUES(?,?,?)', [(entry, src, -amount), (entry, dst, amount)])
        return {'id': entry, 'kind': kind, 'from': src, 'to': dst, 'amount': amount, 'currency': 'DEMO_CREDIT', 'simulated': True}

    def mint(self, account, amount):
        return self.post('issuer', account, amount, 'mint')

    def transfer(self, src, dst, amount):
        name(src)
        return self.post(src, dst, amount, 'transfer')

    def summary(self):
        with self.connection() as db:
            rows = db.execute('SELECT a.name,COALESCE(SUM(p.delta),0) FROM accounts a LEFT JOIN postings p ON a.name=p.account GROUP BY a.name ORDER BY a.name').fetchall()
            minted = db.execute("SELECT COALESCE(SUM(amount),0) FROM entries WHERE kind='mint'").fetchone()[0]
            unbalanced = db.execute('SELECT entry FROM postings GROUP BY entry HAVING SUM(delta)<>0').fetchall()
        balances = dict(rows)
        return {'currency': 'DEMO_CREDIT', 'simulated': True, 'accounts': balances,
                'total_minted': minted, 'circulation': sum(v for k,v in rows if k != 'issuer'),
                'balanced': sum(balances.values()) == 0 and not unbalanced,
                'scope': 'Demo accounting, not a state mint, bank or financial ministry'}

    def transactions(self):
        with self.connection() as db:
            rows = db.execute('SELECT id,kind,src,dst,amount,created FROM entries ORDER BY id DESC LIMIT 100').fetchall()
        return [dict(zip(('id','kind','from','to','amount','created'), row)) for row in rows]

    def economic_report(self):
        result = self.summary()
        result['transactions'] = self.transactions()
        result['metrics'] = {'circulating_units': result['circulation'], 'net_issuer_position': result['accounts']['issuer']}
        return result
