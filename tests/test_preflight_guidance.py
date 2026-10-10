import copy,json,tempfile,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
from cnreconcile.preflight import inspect
from cnreconcile.engine import reconcile
from cnreconcile.report import markdown,html_report
ROOT=Path(__file__).resolve().parents[1]
class InputTests(unittest.TestCase):
    def spec(self):return json.loads((ROOT/'examples/demo.json').read_text('utf-8'))
    def test_preflight_never_opens_pdf_or_calculates_differences(self):
        spec=self.spec();spec['pairs'][0]['evidence']['pdfPath']='missing-private.pdf'
        with patch('cnreconcile.engine.verify_pdf_quote',side_effect=AssertionError('PDF must not open')):
            r=inspect(spec)
        self.assertEqual(r['status'],'declared-fields-valid');self.assertFalse(r['calculationPerformed'])
        self.assertNotIn('results',r);self.assertFalse(r['originalVerified'])
    def test_multiple_missing_fields_and_future_dates(self):
        spec=self.spec();spec['pairs'][0]['reported'].pop('source');spec['pairs'][0]['extracted'].pop('unit')
        r=inspect(spec);self.assertEqual(r['status'],'invalid')
        paths={e['fieldPath'] for e in r['errors']};self.assertIn('pairs[0].reported.source',paths);self.assertIn('pairs[0].extracted.unit',paths)
        spec=self.spec();spec['pairs'][0]['reported']['publishedAt']='2027-01-01';self.assertTrue(inspect(spec)['errors'])
    def test_hints_never_change_status_difference_or_tolerance(self):
        spec=self.spec();r=reconcile(spec)
        matched=r['results'][0];conflict=r['results'][1]
        self.assertEqual(matched['reviewHints'],[]);self.assertEqual(conflict['status'],'value-conflict')
        self.assertTrue(all(h['kind'] in ('review-only','not-inferred') for h in conflict['reviewHints']))
        self.assertIn('非原因结论',markdown(r));self.assertIn('非原因结论',html_report(r,spec))
        spec['pairs'][0]['extracted']['scope']='母公司'
        row=reconcile(spec)['results'][0];self.assertEqual(row['status'],'not-comparable');self.assertIsNone(row['difference'])
        self.assertEqual(row['reviewHints'][0]['field'],'scope');self.assertEqual(row['reviewHints'][0]['kind'],'declared-conflict')
    def test_cli_invalid_input_returns_field_paths_without_output(self):
        with tempfile.TemporaryDirectory() as d:
            spec=self.spec();spec['pairs'][0]['reported'].pop('source');inp=Path(d)/'in.json';inp.write_text(json.dumps(spec),encoding='utf-8')
            p=subprocess.run([sys.executable,'-m','cnreconcile',str(inp),'--dry-run'],capture_output=True)
            self.assertEqual(p.returncode,2);r=json.loads(p.stdout);self.assertEqual(r['status'],'invalid')
            out=Path(d)/'out.json';p=subprocess.run([sys.executable,'-m','cnreconcile',str(inp),'--validate-only','--out',str(out)],capture_output=True)
            self.assertEqual(p.returncode,2);self.assertFalse(out.exists())
