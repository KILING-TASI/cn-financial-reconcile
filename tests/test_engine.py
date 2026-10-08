import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from cnreconcile import reconcile
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
    def spec(self):return json.loads((ROOT/'examples/demo.json').read_text('utf-8'))
    def test_units_and_conflict(self):
        r=reconcile(self.spec())['results'];self.assertEqual(r[0]['difference'],'0.00')
        self.assertEqual(r[0]['status'],'matched-within-rounding');self.assertEqual(r[1]['status'],'value-conflict')
    def test_matching_is_not_page_verification(self):
        r=reconcile(self.spec())['results'][0];self.assertEqual(r['pageEvidenceStatus'],'declared-not-page-verified')
    def test_dimensions_not_forced(self):
        for key,value in [('scope','母公司'),('basis','单季'),('currency','USD')]:
            s=self.spec();s['pairs'][0]['extracted'][key]=value
            self.assertEqual(reconcile(s)['results'][0]['status'],'not-comparable')
    def test_future_and_bad_amounts(self):
        for patch in [dict(publishedAt='2027-01-01'),dict(value='NaN'),dict(value=True),dict(roundingUnit=-1)]:
            s=self.spec();s['pairs'][0]['reported'].update(patch)
            with self.assertRaises(ValueError):reconcile(s)
    def test_declared_rounding_not_hidden_fixed_tolerance(self):
        s=self.spec();s['pairs'][0]['reported'].update(value='1000',unit='元',roundingUnit='1');s['pairs'][0]['extracted'].update(value='1000.4',unit='元',roundingUnit='0')
        self.assertEqual(reconcile(s)['results'][0]['status'],'matched-within-rounding')
        s['pairs'][0]['extracted']['value']='1000.6';self.assertEqual(reconcile(s)['results'][0]['status'],'value-conflict')
    def test_unsupported_units_and_bad_page_rejected(self):
        s=self.spec();s['pairs'][0]['reported']['unit']='%'
        with self.assertRaises(ValueError):reconcile(s)
        s=self.spec();s['pairs'][0]['evidence']['page']=True
        with self.assertRaises(ValueError):reconcile(s)
    def test_missing_evidence_is_explicit(self):
        s=self.spec();s['pairs'][0].pop('evidence');self.assertEqual(reconcile(s)['results'][0]['pageEvidenceStatus'],'evidence-missing')
    def test_cli_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'报告.html';cmd=[sys.executable,'-m','cnreconcile',str(ROOT/'examples/demo.json'),'--format','html','--out',str(out)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0);old=out.read_bytes()
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2);self.assertEqual(old,out.read_bytes())
if __name__=='__main__':unittest.main()
