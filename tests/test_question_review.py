# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import unittest
from cnreconcile.notes_review import review
ROOT=Path(__file__).resolve().parents[1]

class FinancialNotesTest(unittest.TestCase):
    def setUp(self):self.spec=json.loads((ROOT/'examples/expansion-teaching/financial-notes-teaching.json').read_text(encoding='utf-8'))
    def test_restricted_cash_and_unknown_interest(self):
        r=review(self.spec)
        self.assertEqual(r['values']['availableCash'],'1200000000')
        self.assertEqual(r['values']['shortDebtCoverage'],'0.4')
        self.assertIsNone(r['values']['disclosedTotalInterest'])
    def test_negative_and_overrestricted(self):
        self.spec['facts'][1]['value']='21'
        with self.assertRaises(ValueError):review(self.spec)
        self.spec['facts'][1]['value']='-1'
        with self.assertRaises(ValueError):review(self.spec)
    def test_mixed_basis_and_future_unknown(self):
        self.spec['facts'][1]['scope']='母公司'
        with self.assertRaises(ValueError):review(self.spec)
        self.spec['facts'][1]['scope']='合并';self.spec['facts'][-1]['publishedAt']='2026-10-02'
        with self.assertRaises(ValueError):review(self.spec)
    def test_zero_debt(self):
        self.spec['facts'][2]['value']='0'
        self.assertIsNone(review(self.spec)['values']['shortDebtCoverage'])

if __name__=='__main__':unittest.main()
