import json,copy,unittest
from pathlib import Path
from cnreconcile.engine import reconcile
class Tests(unittest.TestCase):
 def spec(self):return json.loads((Path(__file__).resolve().parents[1]/'examples/demo.json').read_text(encoding='utf-8'))
 def test_unknown_schema_rejected_and_legacy_unchanged(self):
  s=self.spec();baseline=reconcile(s);s['inputSchema']='cnreconcile-pairs-v1';self.assertEqual(reconcile(s),baseline);s['inputSchema']='future-999'
  with self.assertRaises(ValueError):reconcile(s)
  self.assertEqual(s['inputSchema'],'future-999')
 def test_equal_money_not_equal_statement_version(self):
  s=self.spec();pair=s['pairs'][0];pair['reported']['statementVersion']='original';pair['extracted']['statementVersion']='restated'
  r=reconcile(s)['results'][0];self.assertEqual(r['status'],'not-comparable');self.assertIsNone(r['difference']);self.assertIn('statementVersion',r['conflictingDimensions'])
 def test_unmatched_explicit_version_does_not_default_to_latest(self):
  s=self.spec();s['pairs'][0]['reported']['statementVersion']='original';s['pairs'][0]['extracted']['statementVersion']=None;r=reconcile(s)['results'][0];self.assertEqual(r['versionComparison'],'different-or-missing-version')
 def test_unit_factor_is_real_conflict_not_rounding_tolerance(self):
  s=self.spec();s['pairs'][0]['reported'].pop('roundingUnit',None);s['pairs'][0]['extracted'].pop('roundingUnit',None);s['pairs'][0]['reported']['unit']='元';s['pairs'][0]['extracted']['unit']='万元';s['pairs'][0]['reported']['value']='100';s['pairs'][0]['extracted']['value']='100'
  r=reconcile(s)['results'][0];self.assertEqual(r['status'],'value-conflict');self.assertEqual(r['difference'],'-999900')
if __name__=='__main__':unittest.main()
