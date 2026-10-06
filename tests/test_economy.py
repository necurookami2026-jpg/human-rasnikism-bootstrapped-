import concurrent.futures
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from madrigal_lab.economy import Economy
from madrigal_lab.finance import Ledger


class EconomyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'demo.sqlite3'
        self.ledger = Ledger(self.path)
        for value in ('lender', 'borrower', 'shop'):
            self.ledger.account(value)
        self.ledger.mint('lender', 100)
        self.economy = Economy(self.ledger)

    def finalise(self, text='A voluntary demonstration record.', parent=None):
        contract = self.economy.create_contract('Review agreement', text, parent)
        self.economy.review_contract(contract['id'], 'Local reviewer', True)
        return self.economy.finalise_contract(contract['id'], 'Local author', True)

    def test_atomic_debt_settlement_and_reopened_portfolio(self):
        loan = self.economy.create_obligation('lender', 'borrower', 40)
        self.assertEqual((loan['state'], loan['outstanding']), ('proposed', 0))
        self.assertEqual(self.ledger.summary()['accounts']['lender'], 100)
        loan = self.economy.lend(loan['id'])
        self.assertEqual((loan['state'], loan['outstanding']), ('funded', 40))
        self.economy.repay(loan['id'], 15)
        report = Economy(Ledger(self.path)).report()
        self.assertEqual(report['accounts'], {'borrower': 25, 'issuer': -100, 'lender': 75, 'shop': 0})
        portfolio = {row['account']: row for row in report['portfolio']}
        self.assertEqual(portfolio['lender']['demo_net_position'], 100)
        self.assertEqual(portfolio['borrower']['demo_net_position'], 0)
        self.assertTrue(report['audit']['balanced'])
        self.assertTrue(report['audit']['obligations_reconciled'])
        settled = self.economy.repay(loan['id'], 25)
        self.assertEqual((settled['state'], settled['outstanding']), ('settled', 0))
        self.assertEqual(self.ledger.summary()['accounts']['lender'], 100)
        with self.assertRaises(ValueError):
            self.economy.repay(loan['id'], 1)

    def test_rejected_lending_and_repayment_leave_both_sides_unchanged(self):
        loan = self.economy.create_obligation('lender', 'borrower', 101)
        before = self.economy.report()
        with self.assertRaises(ValueError):
            self.economy.lend(loan['id'])
        self.assertEqual(self.economy.report(), before)
        loan = self.economy.create_obligation('lender', 'borrower', 50)
        self.economy.lend(loan['id'])
        self.ledger.transfer('borrower', 'shop', 45)
        before = self.economy.report()
        with self.assertRaises(ValueError):
            self.economy.repay(loan['id'], 10)
        with self.assertRaises(ValueError):
            self.economy.repay(loan['id'], 51)
        self.assertEqual(self.economy.report(), before)

    def test_transaction_rolls_back_postings_when_debt_write_fails(self):
        loan = self.economy.create_obligation('lender', 'borrower', 40)
        self.economy.lend(loan['id'])
        before = self.economy.report()
        with self.ledger.connection() as db:
            db.execute('''CREATE TRIGGER reject_repayment BEFORE UPDATE OF paid ON economy_obligations
                BEGIN SELECT RAISE(ABORT, 'injected write failure'); END''')
        with self.assertRaises(sqlite3.IntegrityError):
            self.economy.repay(loan['id'], 10)
        self.assertEqual(self.economy.report(), before)
        self.assertEqual(len(self.ledger.transactions()), 2)

    def test_repayment_budget_reserves_final_settlement_and_rejection_is_atomic(self):
        self.ledger.mint('lender', 300)
        loan = self.economy.create_obligation('lender', 'borrower', 300)
        self.economy.lend(loan['id'])
        for _ in range(255):
            self.economy.repay(loan['id'], 1)
        before = self.economy.report()
        self.assertEqual(before['obligations'][0]['outstanding'], 45)
        with self.assertRaisesRegex(ValueError, 'final repayment'):
            self.economy.repay(loan['id'], 1)
        self.assertEqual(self.economy.report(), before)
        settled = self.economy.repay(loan['id'], 45)
        self.assertEqual((settled['state'], settled['outstanding']), ('settled', 0))
        with self.ledger.connection() as db:
            count = db.execute('SELECT COUNT(*) FROM economy_repayments WHERE obligation=?', (loan['id'],)).fetchone()[0]
        self.assertEqual(count, 256)
        after = self.economy.report()
        with self.assertRaises(ValueError):
            self.economy.repay(loan['id'], 1)
        self.assertEqual(self.economy.report(), after)
        self.assertTrue(after['audit']['balanced'])
        self.assertTrue(after['audit']['obligations_reconciled'])

    def test_concurrent_funding_and_repayment_cannot_double_spend(self):
        loan = self.economy.create_obligation('lender', 'borrower', 30)
        def attempt(method, *args):
            try:
                method(*args)
                return True
            except ValueError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(self.economy.lend, loan['id']), range(2)))
        self.assertEqual(sum(results), 1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(self.economy.repay, loan['id'], 30), range(2)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.economy.report()['obligations'][0]['state'], 'settled')
        self.assertEqual(len(self.ledger.transactions()), 3)

    def test_coupon_is_one_use_annotation_without_money(self):
        coupon = self.economy.create_coupon('Workshop price illustration', 12, 'discount')
        before = self.ledger.summary()
        used = self.economy.redeem_coupon(coupon['id'], 'shop')
        self.assertFalse(used['transfers_units'])
        self.assertEqual((used['state'], used['account']), ('redeemed', 'shop'))
        self.assertEqual(self.ledger.summary(), before)
        with self.assertRaises(ValueError):
            self.economy.redeem_coupon(coupon['id'], 'borrower')
        for kind in ('attack', 'sexual', 'mint', True):
            with self.assertRaises(ValueError):
                self.economy.create_coupon('Unsupported operation', 1, kind)

    def test_contract_assertions_revision_retention_and_receipt(self):
        proposed = self.economy.create_contract('Practice contract', 'Terms before review.')
        for consent in (False, 'yes', 1):
            with self.assertRaises(ValueError):
                self.economy.review_contract(proposed['id'], 'Reviewer', consent)
        with self.assertRaises(ValueError):
            self.economy.finalise_contract(proposed['id'], 'Author', True)
        self.economy.review_contract(proposed['id'], 'Reviewer', True)
        with self.assertRaises(ValueError):
            self.economy.finalise_contract(proposed['id'], 'Author', False)
        first = self.economy.finalise_contract(proposed['id'], 'Author', True)
        self.assertFalse(first['legally_binding'])
        self.assertFalse(first['consent_verified'])
        self.assertEqual(len(first['receipt_sha256']), 64)
        with self.assertRaises(ValueError):
            self.economy.finalise_contract(first['id'], 'Author', True)
        second = self.finalise('Revised terms.', first['id'])
        self.assertEqual((second['version'], second['parent'], second['parent_sha256']), (2, first['id'], first['content_sha256']))
        restored = Economy(Ledger(self.path))
        self.assertTrue(restored.verify_contract(first['id'])['intact'])
        self.assertTrue(restored.verify_contract(second['id'])['intact'])
        self.assertEqual(len(restored.report()['contracts']), 2)

    def test_contract_tamper_blocks_finalisation_and_child_revision(self):
        first = self.finalise()
        second = self.economy.create_contract('Child revision', 'Revised practice.', first['id'])
        with self.ledger.connection() as db:
            db.execute('UPDATE economy_contracts SET body=? WHERE id=?', ('Altered after receipt', first['id']))
        self.assertFalse(self.economy.verify_contract(first['id'])['intact'])
        self.assertFalse(self.economy.verify_contract(second['id'])['intact'])
        self.assertFalse(self.economy.report()['audit']['contracts_intact'])
        with self.assertRaises(ValueError):
            self.economy.review_contract(second['id'], 'Reviewer', True)
        with self.assertRaises(ValueError):
            self.economy.create_contract('Another revision', 'Later terms.', first['id'])

    def test_receipt_and_repayment_tampering_are_reported(self):
        first = self.finalise()
        loan = self.economy.create_obligation('lender', 'borrower', 20)
        self.economy.lend(loan['id'])
        self.economy.repay(loan['id'], 5)
        with self.ledger.connection() as db:
            db.execute('UPDATE economy_contracts SET receipt_sha256=? WHERE id=?', ('0' * 64, first['id']))
            db.execute('UPDATE economy_repayments SET amount=4 WHERE obligation=?', (loan['id'],))
        self.assertFalse(self.economy.verify_contract(first['id'])['intact'])
        audit = self.economy.report()['audit']
        self.assertTrue(audit['balanced'])
        self.assertFalse(audit['obligations_reconciled'])
        self.assertFalse(audit['contracts_intact'])

    def test_bounds_reserved_issuer_and_unknown_accounts(self):
        for amount in (True, False, 0, -1, 1.0, 10**12 + 1):
            with self.assertRaises(ValueError):
                self.economy.create_obligation('lender', 'borrower', amount)
        for src, dst in (('issuer', 'borrower'), ('lender', 'issuer'), ('missing', 'borrower'), ('lender', 'lender')):
            with self.assertRaises(ValueError):
                self.economy.create_obligation(src, dst, 1)
        for record_id in (True, 0, -1, 257, 1.0):
            with self.assertRaises(ValueError):
                self.economy.lend(record_id)
        with self.assertRaises(ValueError):
            self.economy.create_contract('Title', '🌿' * 4097)
        with self.assertRaises(ValueError):
            self.economy.create_contract('Bad\nlabel', 'Text')
        for _ in range(256):
            self.economy.create_coupon('Finite coupon', 1)
        with self.assertRaises(ValueError):
            self.economy.create_coupon('Overflow', 1)
        self.assertEqual(len(self.economy.report()['coupons']), 256)

    def test_database_and_sidecar_symlinks_are_rejected(self):
        linked = Path(self.temp.name) / 'linked.sqlite3'
        linked.symlink_to(self.path)
        with patch.object(self.ledger, 'path', linked):
            with self.assertRaises(ValueError):
                Economy(self.ledger)
        sidecar = Path(str(self.path) + '-journal')
        sidecar.symlink_to(Path(self.temp.name) / 'outside')
        with self.assertRaises(ValueError):
            self.economy.report()


if __name__ == '__main__':
    unittest.main()
