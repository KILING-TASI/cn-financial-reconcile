import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TestFeedback(unittest.TestCase):
    def cli(self,*args,no_site=False):
        return subprocess.run([sys.executable,*(["-S"] if no_site else []),*args],cwd=ROOT,capture_output=True,encoding="utf-8")

    def test_json_and_saved_teaching_guidance(self):
        normal=self.cli("-m","cnreconcile","examples/demo.json")
        self.assertEqual(normal.returncode,0)
        self.assertEqual(json.loads(normal.stdout)["rulesVersion"],"amount-dimensions-2")
        self.assertEqual(normal.stderr,"")
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"报告.html"
            args=("-m","cnreconcile","examples/demo.json","--format","html","--out",str(target))
            first=self.cli(*args)
            self.assertEqual(first.returncode,0)
            self.assertEqual(first.stdout,"")
            self.assertIn("教学",first.stderr)
            self.assertIn(str(target),first.stderr)
            old=hashlib.sha256(target.read_bytes()).hexdigest()
            second=self.cli(*args)
            self.assertEqual(second.returncode,2)
            self.assertIn("换一个新名字",second.stderr)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),old)

    def test_missing_pdf_retains_parseable_unknown_and_install_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec=json.loads((ROOT/"examples/demo.json").read_text("utf-8"))
            spec["pairs"][0]["evidence"]["pdfPath"]=str(Path(tmp)/"not-installed.pdf")
            source=Path(tmp)/"input.json";source.write_text(json.dumps(spec),encoding="utf-8")
            proc=self.cli("-m","cnreconcile",str(source),no_site=True)
            self.assertEqual(proc.returncode,0)
            self.assertEqual(json.loads(proc.stdout)["results"][0]["pageEvidenceStatus"],"pdf-component-missing")
            self.assertIn('python -m pip install ".[pdf]"',proc.stderr)
            self.assertNotIn(str(Path(tmp)/"not-installed.pdf"),proc.stderr)

    def test_report_directories_and_private_invalid_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            for module,source,html in [("cnreconcile.dividend_observation","examples/dividend-teaching-v2.json","报告.html"),("cnreconcile.version_review","validation/guozhong-version-public-input.json","版本对照.html")]:
                target=Path(tmp)/module
                args=("-m",module,source,"--out-dir",str(target))
                proc=self.cli(*args);self.assertEqual(proc.returncode,0,proc.stderr)
                self.assertEqual(proc.stdout,"");self.assertIn(html,proc.stderr)
                before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
                self.assertEqual(self.cli(*args).returncode,2)
                self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()})
            source=Path(tmp)/"invalid.json";source.write_text('{"SECRET_PRIVATE_KEY":',encoding="utf-8")
            target=Path(tmp)/"bad.html"
            proc=self.cli("-m","cnreconcile",str(source),"--out",str(target))
            self.assertEqual(proc.returncode,2);self.assertFalse(target.exists())
            self.assertNotIn("SECRET_PRIVATE_KEY",proc.stderr);self.assertIn("核对schema",proc.stderr)
