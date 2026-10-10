"""Run bounded teaching scenarios through the real CLI; new output directory only."""
import argparse, copy, hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def scenarios():
    amount = json.loads((ROOT / "examples/demo.json").read_text("utf-8"))
    dividend = json.loads((ROOT / "examples/dividend-teaching-v2.json").read_text("utf-8"))
    cases = []
    def add(name, kind, spec, expected, reason, error=None):
        cases.append(dict(name=name, kind=kind, input=spec, expected=expected, reason=reason, error=error))
    add("amount-demo", "amount", amount, {"results.0.difference":"0.00", "results.0.status":"matched-within-rounding", "results.0.pageEvidenceStatus":"declared-not-page-verified", "results.1.status":"value-conflict"}, "1亿元=10000万元；相同金额不证明原页已核。复用原教学正例。")
    for name, value, status in [("rounding-boundary", "1000.5", "matched-within-rounding"), ("rounding-outside", "1000.5001", "value-conflict")]:
        s=copy.deepcopy(amount); s["pairs"]=s["pairs"][:1]
        s["pairs"][0]["reported"].update(value="1000", unit="元", roundingUnit="1")
        s["pairs"][0]["extracted"].update(value=value, unit="元", roundingUnit="0")
        add(name,"amount",s,{"results.0.status":status,"results.0.roundingTolerance":"0.5"},"1000元四舍五入至元的半单位为0.5元；边界内含，超过0.0001元即冲突。")
    s=copy.deepcopy(amount); s["pairs"]=s["pairs"][:1]
    for key,version in [("reported","original"),("extracted","restated")]:s["pairs"][0][key]["statementVersion"]=version
    add("same-money-different-version","amount",s,{"results.0.status":"not-comparable","results.0.difference":None,"results.0.conflictingDimensions":["statementVersion"]},"相同金额的原版与重述版不能自动裁为同一事实。")
    s=copy.deepcopy(amount);s["pairs"]=s["pairs"][:1];s["pairs"][0].pop("evidence")
    add("missing-page","amount",s,{"results.0.status":"matched-within-rounding","results.0.pageEvidenceStatus":"evidence-missing"},"移除原页声明，数值仍匹配但证据必须缺失。")
    s=copy.deepcopy(amount);s["pairs"][0]["reported"]["publishedAt"]="2027-01-01"
    add("future-disclosure","amount",s,{},"晚于截止日必须失败且不留报告。","事实披露晚于截止日")
    add("dividend-demo","dividend",dividend,{"cashSurplus":"800000","profitLessDeclaredOneOff":"800000","coverage.declaredDividend.cashSurplusCoverage":"1.6","coverage.declaredDividend.profitCoverage":"2","coverage.paidDividend.profitCoverage":None,"coverage.paidDividend.profitCoverageStatus":"not-applicable-to-paid-dividend"},"120−40=80万元；80/50=1.6；100/50=2。2025支付30万元归属2024，不能与2025宣告50合计或套2025利润。")
    s=copy.deepcopy(dividend);s["facts"]["declaredDividend"]["attributablePeriod"]="2024-12-31"
    add("declaration-other-year","dividend",s,{"coverage.declaredDividend.status":"period-not-comparable","coverage.declaredDividend.profitCoverage":None},"把宣告归属改为2024，2025利润及现金不能强行评价它。")
    s=copy.deepcopy(dividend);s["facts"]["capitalExpenditure"]=None
    add("missing-capex","dividend",s,{"cashSurplus":None,"coverage.declaredDividend.cashSurplusCoverage":None},"缺资本开支，不能把全部经营现金流当现金结余。")
    s=copy.deepcopy(dividend);s["facts"]["oneOffProfit"]["profitAttribution"]="all-owners"
    add("profit-ownership-mismatch","dividend",s,{"profitLessDeclaredOneOff":None,"coverage.declaredDividend.profitCoverage":"2"},"一次性项归属不一致禁止减除；独立的归母利润与宣告分红仍可观察。")
    s=copy.deepcopy(dividend);s["facts"]["declaredDividend"]["recipientAttribution"]="all-owners"
    add("recipient-mismatch","dividend",s,{"coverage.declaredDividend.profitCoverage":None,"coverage.declaredDividend.cashSurplusCoverage":"1.6"},"股息受益归属不同，利润覆盖未知；现金计算独立。")
    s=copy.deepcopy(dividend);s["facts"]["profit"]["statementVersion"]="restated-v2"
    add("dividend-version-conflict","dividend",s,{},"未选定同一声明版本，失败且不创建结果目录。","版本不同")
    return cases

def lookup(value,path):
    for part in path.split("."):value=value[int(part)] if isinstance(value,list) else value[part]
    return value

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    rows=[]
    for case in scenarios():
        folder=out/case["name"];folder.mkdir()
        source=folder/"input.json";source.write_text(json.dumps(case["input"],ensure_ascii=False,indent=2),encoding="utf-8")
        (folder/"expected.json").write_text(json.dumps({k:case[k] for k in ("expected","reason","error")},ensure_ascii=False,indent=2),encoding="utf-8")
        target=folder/("result.json" if case["kind"]=="amount" else "report")
        cmd=[sys.executable,"-m","cnreconcile" if case["kind"]=="amount" else "cnreconcile.dividend_observation",str(source)]
        cmd += ["--out",str(target)] if case["kind"]=="amount" else ["--out-dir",str(target)]
        proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,encoding="utf-8")
        result=None
        if case["error"]:
            assert proc.returncode != 0 and case["error"] in proc.stderr and not target.exists(), (case["name"],proc.stderr)
        else:
            assert proc.returncode == 0,(case["name"],proc.stderr)
            result=json.loads((target if case["kind"]=="amount" else target/"result.json").read_text("utf-8"))
            for path,expected in case["expected"].items():assert lookup(result,path)==expected,(case["name"],path,lookup(result,path),expected)
            if case["kind"]=="amount":
                htmlcmd=cmd[:-2]+["--format","html","--out",str(folder/"report.html")]
                rendered=subprocess.run(htmlcmd,cwd=ROOT,capture_output=True,encoding="utf-8")
                assert rendered.returncode==0,rendered.stderr
        row=dict(name=case["name"],passed=True,exitCode=proc.returncode,stderr=proc.stderr,methodVersion=result.get("rulesVersion",result.get("methodVersion")) if result else "rejected-before-result",inputSha256=hashlib.sha256(source.read_bytes()).hexdigest())
        (folder/"actual.json").write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding="utf-8");rows.append(row)
    receipt=dict(batch="bounded-teaching-scenarios-20261010",python=sys.version,baseCommit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),cases=rows,limitations=["教学情景，不扩大真实公司样本；没有PDF认证", "HTML仅实际生成，未做浏览器视觉验收", "失败场景没有结果文件；本入口拒绝已有输出目录"])
    (out/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out-dir",type=Path,required=True)
    args=parser.parse_args();run(args.out_dir.resolve())
