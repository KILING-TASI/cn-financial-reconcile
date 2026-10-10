import copy
import json
from pathlib import Path
import tempfile
import unittest
from cnreconcile.version_review import calculate


class TestVersionReview(unittest.TestCase):
    def setUp(self):
        self.s=json.loads((Path(__file__).parents[1]/'validation/guozhong-version-public-input.json').read_text('utf-8'))
    def test_public_pair_does_not_claim_original_verified_or_latest(self):
        before=copy.deepcopy(self.s);r=calculate(self.s)
        self.assertEqual(self.s,before)
        self.assertEqual(r['latestVersionStatus'],'not-certified')
        self.assertTrue(all(x['evidenceStatus']['before']=='declared-not-page-verified' for x in r['fieldPairs']))
        self.assertEqual([x['status'] for x in r['fieldPairs']],['changed','unchanged'])
    def test_change_not_in_notice_scope_refused(self):
        self.s['relations'][0]['fields']=['another-field']
        with self.assertRaises(ValueError):calculate(self.s)
    def test_original_file_sha_not_notice_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.pdf';p.write_bytes(b'not the registered original')
            self.s['documents'][0]['pdfPath']=str(p)
            with self.assertRaises(ValueError):calculate(self.s)
    def test_unknown_version_and_unbound_value_refused(self):
        self.s['methodVersion']='future'
        with self.assertRaises(ValueError):calculate(self.s)
        self.s['methodVersion']='bound-selected-occurrences-1';self.s['fieldPairs'][0]['before']['value']='99%'
        with self.assertRaises(ValueError):calculate(self.s)
