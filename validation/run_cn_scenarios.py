"""Three CN teaching scenario families, with official historical rules in CN_SCENARIOS.md."""
import argparse, copy, json
from pathlib import Path
from run_scenarios import ROOT, run

def scenarios():
    demo=json.loads((ROOT/"examples/demo.json").read_text("utf-8"))
    div=json.loads((ROOT/"examples/dividend-teaching-v2.json").read_text("utf-8"))
    cases=[]
    def add(name,kind,spec,expected,reason,error=None):
        cases.append(dict(name=name,kind=kind,input=spec,expected=expected,reason=reason,error=error))
    s=copy.deepcopy(demo);s["pairs"]=[]
    for metric,scope,basis in [("营业收入","合并","累计"),("营业收入","母公司","累计"),("营业收入","合并","单季"),("净利润","合并","累计")]:
        pair=copy.deepcopy(demo["pairs"][0]);pair.pop("evidence");pair["reported"].update(metric="营业收入" if metric=="营业收入" else "归属于母公司所有者的净利润",value="1",unit="亿元",roundingUnit="0");pair["extracted"].update(metric=metric,scope=scope,basis=basis,value="100000000",unit="元",roundingUnit="0");s["pairs"].append(pair)
    add("cn-interim-dimensions","amount",s,{"results.0.status":"matched-within-rounding","results.0.difference":"0","results.1.conflictingDimensions":["scope"],"results.2.conflictingDimensions":["basis"],"results.3.conflictingDimensions":["metric"]},"同为1亿元：同口径匹配；母公司不同于合并、单季不同于累计、全部净利润不同于归母。CAS32第4/5条，CAS33第35条。无原页保持证据缺失。")
    s=copy.deepcopy(div);s["facts"]["profit"].update(value="1000",unit="万元");s["facts"]["oneOffProfit"].update(value="120",unit="万元",profitAttribution="parent-owners",taxBasis="after-tax")
    add("cn-oneoff-net-parent","dividend",s,{"profitLessDeclaredOneOff":"8800000","profitAdjustmentStatus":"declared-comparable-profit"},"教学税前非经常200万元、税影响50万元、少数股东影响30万元：已独立整理归母税后120万元；1000−120=880万元。工具不计算税率，不认证非经常分类。CSRC2023-65第八项。")
    s=copy.deepcopy(s);s["facts"]["oneOffProfit"].update(value="200",taxBasis="before-tax")
    add("cn-oneoff-gross-unknown","dividend",s,{"profitLessDeclaredOneOff":None,"profitAdjustmentStatus":"ownership-or-tax-basis-unknown-or-inconsistent"},"仅有税前200万元，不能直接从归母税后1000万元减除；税与少数权益不能缺省为零。")
    s=copy.deepcopy(div);s["facts"]["paidDividend"]=None;s["facts"]["declaredDividend"]["source"]="教学董事会预案50万元；股东大会尚未批准；不是实际派息。阶段仅由来源文字说明，不由本工具核验。"
    add("cn-proposal-not-paid","dividend",s,{"coverage.declaredDividend.cashSurplusCoverage":"1.6","coverage.paidDividend.status":"missing","amounts.paidDividend":None},"预案仅作为选定拟分红金额观察：80/50=1.6。无派息证据不填支付零；本工具不支持阶段状态机、不认证批准。CAS32第8条第9项。")
    s=copy.deepcopy(s);s["facts"]["declaredDividend"]["source"]="教学股东大会已批准50万元，尚未实施；没有支付凭据；阶段仅来源说明。"
    add("cn-approved-unpaid","dividend",s,{"coverage.paidDividend.status":"missing","amounts.paidDividend":None},"批准方案与支付事实分别保留：批准不能自动补出现金支付，本工具不认证会议决议。")
    s=copy.deepcopy(div);s["facts"]["paidDividend"].update(value="30",unit="万元",source="教学拆分：筹资混合支出45万元=纯股息30万元+利息15万元；仅独立确认的纯股息30填本项，不含利息。")
    add("cn-paid-excluding-interest","dividend",s,{"amounts.paidDividend":"300000","coverage.paidDividend.cashSurplusCoverage":"2.666666666666666666666666667"},"45−15=30万元纯股息；80/30=8/3。拆分由输入证据完成，工具不从45自动推断30；财政部2023-11-10解释混合行含股息/利润/利息。")
    s=copy.deepcopy(div);s["facts"]["paidDividend"].update(value="45",metric="dividendsProfitsAndInterestPaid")
    add("cn-composite-payment-rejected","dividend",s,{},"含利息混合行保留真实指标名称，不能冒充paidDividend；拒绝且目标目录不存在。若调用者改名，现有工具不能认证其真实性，必须人工核对。","指标语义冲突")
    s=copy.deepcopy(div);s["facts"]["approvedDividend"]=s["facts"].pop("declaredDividend")
    add("cn-stage-schema-rejected","dividend",s,{},"未实现approvedDividend独立阶段接口，不允许静默新增事实槽位；拒绝且目标目录不存在。","事实字段未知")
    return cases

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out-dir",type=Path,required=True);a=p.parse_args()
    out=a.out_dir.resolve()
    receipt=run(out,scenarios())
    receipt.update(batch="cn-three-scenario-families-20261010",scenarioFamilies=3,sourceIndex="validation/cn-sources-20261010.json",verifiedAt="2026-10-10",timezone="Asia/Shanghai")
    (out/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
