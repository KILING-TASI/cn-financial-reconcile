import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scenario_runner", ROOT / "validation/run_scenarios.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class TestCliScenarios(unittest.TestCase):
    def test_real_cli_decisions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "batch"
            receipt = runner.run(out)
            self.assertEqual(len(receipt["cases"]), 12)
            self.assertTrue(all(case["passed"] for case in receipt["cases"]))
            before = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob("*") if p.is_file()}
            with self.assertRaises(FileExistsError):
                runner.run(out)
            after = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_cn_three_families(self):
        import json
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "cn"
            cmd = [sys.executable, str(ROOT / "validation/run_cn_scenarios.py"), "--out-dir", str(out)]
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            receipt = json.loads((out / "receipt.json").read_text("utf-8"))
            self.assertEqual(receipt["scenarioFamilies"], 3)
            self.assertEqual(len(receipt["cases"]), 8)
            self.assertTrue(all(c["passed"] for c in receipt["cases"]))
            before = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob("*") if p.is_file()}
            self.assertNotEqual(subprocess.run(cmd, cwd=ROOT, capture_output=True).returncode, 0)
            after = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
