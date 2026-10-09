import copy,json,unittest
from pathlib import Path
from cnreconcile.dividend_observation import calculate
class TestDividend(unittest.TestCase):
 def setUp(self):self.s=json.loads((Path(__file__).parents[1]/'examples/dividend-teaching-v2.json').read_text('utf-8'))
 def test_declared_and_paid_separate(self):
  r=calculate(self.s);self.assertEqual(r['coverage']['declaredDividend']['cashSurplusCoverage'],'1.6');self.assertNotEqual(r['coverage']['paidDividend']['cashSurplusCoverage'],'1.6')
 def test_missing(self):
  self.s['facts']['capitalExpenditure']=None
  self.assertIsNone(calculate(self.s)['cashSurplus'])
 def test_nonpositive(self):
  for v in [0, -1]:
   s=copy.deepcopy(self.s);s['facts']['operatingCashFlow']['value']=v
   self.assertIsNone(calculate(s)['coverage']['declaredDividend']['cashSurplusCoverage'])
  self.s['facts']['declaredDividend']['value']=0
  self.assertIsNone(calculate(self.s)['coverage']['declaredDividend']['cashSurplusCoverage'])
 def test_period_version_scope(self):
  for k,v in [('period','2024-12-31'),('statementVersion','restated-v2'),('scope','parent-only')]:
   s=copy.deepcopy(self.s);s['facts']['profit'][k]=v
   with self.assertRaises(ValueError):calculate(s)
 def test_other_year_declaration(self):
  self.s['facts']['declaredDividend']['attributablePeriod']='2024-12-31'
  self.assertEqual(calculate(self.s)['coverage']['declaredDividend']['status'],'period-not-comparable')
 def test_mixed_units_same_amount(self):
  self.s['facts']['capitalExpenditure'].update(unit='元',value=400000)
  self.assertEqual(calculate(self.s)['cashSurplus'],'800000')
 def test_report_new_output_and_escape(self):
  import tempfile
  from cnreconcile.dividend_observation import publish
  with tempfile.TemporaryDirectory() as tmp:
   self.s['facts']['profit']['source']='<script>alert(1)</script>'
   out=Path(tmp)/'new';publish(self.s,out)
   self.assertNotIn('<script>alert(1)</script>',(out/'报告.html').read_text('utf-8'))
   with self.assertRaises(FileExistsError):publish(self.s,out)
 def test_each_metric_must_match_slot(self):
  for key in self.s['facts']:
   s=copy.deepcopy(self.s);s['facts'][key]['metric']='revenue'
   with self.subTest(key=key),self.assertRaises(ValueError):calculate(s)
 def test_explicit_versions_refused(self):
  for key in ['inputSchema','methodVersion']:
   for value in [None,'future-v999','dividend-observation-1']:
    s=copy.deepcopy(self.s);s[key]=value
    with self.subTest(key=key,value=value),self.assertRaises(ValueError):calculate(s)
 def test_old_unspecified_profit_basis_is_unknown(self):
  s=json.loads((Path(__file__).parents[1]/'examples/dividend-teaching.json').read_text('utf-8'))
  r=calculate(s);self.assertIsNone(r['profitLessDeclaredOneOff']);self.assertIsNone(r['coverage']['declaredDividend']['profitCoverage']);self.assertEqual(r['methodVersion'],'dividend-observation-2')
 def test_profit_oneoff_ownership_and_tax(self):
  for key,value in [('profitAttribution','all-owners'),('taxBasis','before-tax'),('profitAttribution',None)]:
   s=copy.deepcopy(self.s);s['facts']['oneOffProfit'][key]=value
   with self.subTest(key=key,value=value):self.assertIsNone(calculate(s)['profitLessDeclaredOneOff'])
  self.s['facts']['declaredDividend']['recipientAttribution']='all-owners'
  self.assertIsNone(calculate(self.s)['coverage']['declaredDividend']['profitCoverage'])
 def test_version_selection_stays_unverified(self):
  self.assertEqual(calculate(self.s)['versionSelectionStatus'],'declared-not-original-verified')
