import hashlib,io,json,subprocess,unittest,zipfile
from pathlib import Path
class Tests(unittest.TestCase):
    def test_git_archive_case_hashes_match_even_with_windows_autocrlf(self):
        root=Path(__file__).parents[1]
        if not (root/'.git').exists():self.skipTest('archive test requires Git checkout; installed artifacts verified separately')
        raw=subprocess.check_output(['git','-c','core.autocrlf=true','archive','--format=zip','HEAD'],cwd=root)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            prefix='examples/midea-cash-coverage-20261010/'
            receipt=json.loads(z.read(prefix+'receipt.json'))
            for name,want in receipt['filesSha256'].items():self.assertEqual(hashlib.sha256(z.read(prefix+name)).hexdigest(),want,name)
