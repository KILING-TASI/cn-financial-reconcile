"""Reproduce a selected public annual-report question; PDF stays local/private."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cnreconcile.dividend_observation import publish

def reproduce(pdf,out,download=False):
    source=Path(__file__).resolve().parents[1]/'examples/midea-dividend-source-input.json'
    spec=json.loads(source.read_text('utf-8'))
    expected={f['evidence']['documentSha256'] for f in spec['facts'].values()};assert len(expected)==1
    url=spec['facts']['operatingCashFlow']['source']
    if out.exists():raise ValueError('结果目录已存在；请使用新目录，保留旧案例')
    if download:
        with urllib.request.urlopen(url,timeout=60) as response:raw=response.read(64*1024*1024+1)
    else:
        if pdf.stat().st_size>64*1024*1024:raise ValueError('PDF超过64MiB')
        raw=pdf.read_bytes()
    if len(raw)>64*1024*1024 or hashlib.sha256(raw).hexdigest() not in expected:raise ValueError('PDF原始字节摘要与选定2025年报不一致；不改用其他版本或替代材料')
    out.mkdir(parents=True,exist_ok=False);private=out/'private-original.pdf';private.write_bytes(raw)
    for f in spec['facts'].values():f['evidence']['pdfPath']=str(private.resolve())
    try:
        result=publish(spec,out/'report')
        # Publishable projection excludes paths and does not claim it can recheck without PDF.
        public=json.loads(json.dumps(spec))
        for f in public['facts'].values():f['evidence'].pop('pdfPath',None)
        (out/'public-input.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
        receipt=dict(status='selected-question-completed',question='美的集团2025年合并经营现金流减选定资本开支，能否覆盖该年宣告分红？',
            sourceUrl=url,documentSha256=hashlib.sha256(raw).hexdigest(),asOf=spec['asOf'],methodVersion=result['methodVersion'],verification=result['verification'],
            referenceCashSurplus='42204041000',referenceDeclaredCoverage='1.304178585348699171882460862',latestVersionVerified=False,
            limitations=['完整流程仅覆盖这一个年度现金覆盖问题，不是完整公司估值或投资决策','原PDF仅本地留存，不随公开包再分发','合并现金不等于母公司可分配现金，覆盖不证明实际或未来可支付'])
        assert result['cashSurplus']==receipt['referenceCashSurplus']
        assert result['coverage']['declaredDividend']['cashSurplusCoverage']==receipt['referenceDeclaredCoverage']
        assert all(v=='quote-found-on-page' for v in result['verification'].values())
        receipt['methodSha256']={name:hashlib.sha256((source.parents[1]/name).read_bytes()).hexdigest() for name in ['cnreconcile/dividend_observation.py','cnreconcile/engine.py','tools/reproduce_midea_case.py']}
        receipt['filesSha256']={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p!=private}
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        return receipt
    except Exception:
        (out/'INCOMPLETE.txt').write_text('案例未完成；保留失败材料，不作为已核验交付。',encoding='utf-8');raise

if __name__=='__main__':
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='选定美的2025年报现金覆盖问题复现；需要pypdf，原件不公开打包')
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--pdf',type=Path);g.add_argument('--download',action='store_true',help='显式从已登记深交所URL下载一次，不自动兜底')
    p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(reproduce(a.pdf,a.out_dir,a.download),ensure_ascii=False,indent=2))
    except (ValueError,OSError,ImportError) as e:p.exit(2,str(e)+'\n')
