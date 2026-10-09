"""Bounded dividend coverage observation, not a payout forecast."""
import argparse
import json
from pathlib import Path
from .engine import validate_fact

INPUT_SCHEMA = 'cnreconcile-dividend-v1'
METHOD_VERSION = 'dividend-observation-2'
METRICS = ('operatingCashFlow', 'capitalExpenditure', 'profit', 'oneOffProfit', 'declaredDividend', 'paidDividend')


def calculate(spec):
    if not isinstance(spec, dict):
        raise ValueError('输入须为对象')
    if set(spec) - {'inputSchema', 'methodVersion', 'exampleType', 'asOf', 'companyType', 'facts'}:
        raise ValueError('未知输入字段，不能忽略后继续计算')
    if 'inputSchema' in spec and spec['inputSchema'] != INPUT_SCHEMA:
        raise ValueError('未知输入schema，须显式转换')
    if 'methodVersion' in spec and spec['methodVersion'] != METHOD_VERSION:
        raise ValueError('方法版本不支持，不能静默改用本轮方法')
    if spec.get('exampleType') != 'teaching-only':
        raise ValueError('本批先限定教学输入；尚未完成公开公司原文样本验收')
    from datetime import date
    cutoff = spec['asOf']
    if date.fromisoformat(cutoff).isoformat() != cutoff:
        raise ValueError('截止日期无效')
    if spec.get('companyType') != 'non-financial':
        raise ValueError('首版限定非金融企业')
    facts = spec['facts']
    if not isinstance(facts, dict) or set(facts) - set(METRICS):
        raise ValueError('事实字段未知或结构无效')
    values, states = {}, {}
    keys = METRICS
    anchor = None
    for key in keys:
        fact = facts.get(key)
        if fact is None:
            values[key] = None
            states[key] = 'missing'
            continue
        if not isinstance(fact, dict) or fact.get('metric') != key:
            raise ValueError('指标语义冲突：' + key + '须声明metric=' + key)
        amount, _ = validate_fact(fact, cutoff)
        version = fact.get('statementVersion')
        if not isinstance(version, str) or not version.strip():
            raise ValueError('须声明已选用的报表/公告版本')
        dimensions = tuple(fact[k] for k in ('entity', 'scope', 'currency'))
        if anchor is None:
            anchor = dimensions
        if dimensions != anchor:
            raise ValueError('主体、合并范围或币种不同，不能计算覆盖关系')
        if fact.get('basis') != 'annual':
            raise ValueError('首版仅支持明确年度金额')
        values[key] = amount
        states[key] = 'teaching-not-original-verified'
        if key in ('capitalExpenditure', 'declaredDividend', 'paidDividend') and amount < 0:
            raise ValueError('资本开支和分红须为非负现金流出金额')
        if fact.get('attributablePeriod') is not None:
            attributed = fact['attributablePeriod']
            if date.fromisoformat(attributed).isoformat() != attributed or attributed > fact['publishedAt']:
                raise ValueError('分红所属年度日期无效或晚于披露日')
    # All performance/cash measures must share reporting period and selected statement version.
    operating = [facts[k] for k in keys[:4] if facts.get(k)]
    if len({(f['period'], f['statementVersion']) for f in operating}) > 1:
        raise ValueError('经营指标期间或更正版本不同')
    # Consolidation alone does not establish who owns the profit or whether
    # the exceptional gain is pre-tax/after-tax. Unknown is not a default.
    for key in ('profit', 'oneOffProfit'):
        fact = facts.get(key)
        if fact:
            if fact.get('profitAttribution') not in (None, 'unknown', 'parent-owners', 'all-owners'):
                raise ValueError('利润归属口径不支持')
            if fact.get('taxBasis') not in (None, 'unknown', 'before-tax', 'after-tax'):
                raise ValueError('利润税前税后口径不支持')
    declaration = facts.get('declaredDividend')
    if declaration and declaration.get('recipientAttribution') not in (None, 'unknown', 'parent-owners', 'all-owners'):
        raise ValueError('分红受益人归属口径不支持')
    ratios = {}
    ocf, capex = values['operatingCashFlow'], values['capitalExpenditure']
    free = None if ocf is None or capex is None else ocf - capex
    for key in ('declaredDividend', 'paidDividend'):
        fact = facts.get(key)
        status = 'missing'
        ratio = None
        if fact:
            # Dividend fiscal attribution is different from cash payment period.
            reference = fact.get('attributablePeriod') if key == 'declaredDividend' else fact['period']
            if not operating or reference != operating[0]['period']:
                status = 'period-not-comparable'
            elif free is None:
                status = 'cash-input-missing'
            elif free <= 0 or values[key] <= 0:
                status = 'nonpositive-denominator-or-cash-surplus'
            else:
                ratio = str(free / values[key])
                status = 'observed-coverage'
        profit_ratio = None
        profit_status = 'profit-or-dividend-missing'
        if key == 'declaredDividend' and fact and operating and fact.get('attributablePeriod') == operating[0]['period']:
            p = facts.get('profit')
            profit_status = 'ownership-or-tax-basis-unknown-or-inconsistent'
            if p and p.get('taxBasis') == 'after-tax' and p.get('profitAttribution') in ('parent-owners', 'all-owners') and p.get('profitAttribution') == fact.get('recipientAttribution'):
                profit_status = 'nonpositive-profit-or-dividend'
                if values['profit'] > 0 and values[key] > 0:
                    profit_status = 'declared-comparable-profit'
                    profit_ratio = str(values['profit'] / values[key])
        ratios[key] = dict(status=status, cashSurplusCoverage=ratio, profitCoverage=profit_ratio, profitCoverageStatus=profit_status)
    p, exceptional = facts.get('profit'), facts.get('oneOffProfit')
    adjustment_status = 'profit-or-oneoff-missing'
    adjusted = None
    if p and exceptional:
        adjustment_status = 'ownership-or-tax-basis-unknown-or-inconsistent'
        if p.get('taxBasis') == exceptional.get('taxBasis') == 'after-tax' and p.get('profitAttribution') in ('parent-owners', 'all-owners') and p.get('profitAttribution') == exceptional.get('profitAttribution'):
            adjusted = values['profit'] - values['oneOffProfit']
            adjustment_status = 'declared-comparable-profit'
    declared_ratio = ratios['declaredDividend']['cashSurplusCoverage']
    assessment = '资料或口径不足，不能判断当年宣告分红的现金覆盖。'
    if declared_ratio is not None:
        assessment = ('本组教学金额中，扣除资本开支后的经营现金结余足以覆盖当年宣告分红。' if free >= values['declaredDividend'] else
                      '本组教学金额中，扣除资本开支后的经营现金结余不足以覆盖当年宣告分红；这不等于公司无法支付。')
    elif ratios['declaredDividend']['status'] == 'nonpositive-denominator-or-cash-surplus':
        assessment = '本组现金结余或分红金额非正，不能给出安全覆盖倍数。'
    return dict(type='dividend-sustainability-observation', inputSchema=INPUT_SCHEMA, methodVersion=METHOD_VERSION,
                versionSelectionStatus='declared-not-original-verified',
                profitAdjustmentStatus=adjustment_status, asOf=cutoff, currency=anchor[2] if anchor else None,
                amounts={k: None if v is None else str(v) for k, v in values.items()},
                verification=states, cashSurplus=None if free is None else str(free),
                profitLessDeclaredOneOff=None if adjusted is None else str(adjusted), coverage=ratios,
                conclusion=assessment + ' 这是当期观察，不承诺未来分红；宣告与实际支付分开看。',
                limitations=['金额和已核状态来自输入声明，未独立认证原文；资本开支定义须在来源中说明',
                             '经营现金流减资本开支是本次观察代理，不等同可分配利润或严格FCFF',
                             '一次性收益仅在税后和利润归属口径已声明一致时调整；不验证会计分类，不预测未来分红，不统一打分',
                             '相同版本文字不证明原文同版；不自动选择更正版本，未核原文时保持声明未验证',
                             '合并经营现金结余不是母公司可分配现金；覆盖倍数不证明能支付分红'])


def publish(spec, out):
    import html
    result = calculate(spec)
    out = Path(out)
    if out.exists():
        raise FileExistsError('请另存新目录')
    text = '# 分红可持续性观察\n\n**教学金额，不是实际公司判断。**\n\n' + result['conclusion']
    def money(value):
        from decimal import Decimal
        return '未知' if value is None else format(Decimal(value), ',.2f') + '基本货币单位（' + result['currency'] + '）'
    text += '\n\n经营现金流减资本开支为%s；扣除输入所列一次性收益后的利润为%s。缺失项不按零处理。' % (money(result['cashSurplus']), money(result['profitLessDeclaredOneOff']))
    text += '\n\n方法版本：' + METHOD_VERSION + '。税后及利润归属未声明一致时，利润调整与利润覆盖保持未知；已选报表版本尚未核验原文。'
    states = {'missing': '缺少分红金额', 'period-not-comparable': '所属年度或支付期间不一致，不能比较',
              'cash-input-missing': '缺少经营现金流或资本开支',
              'nonpositive-denominator-or-cash-surplus': '现金结余或分红金额非正，不计算安全覆盖倍数',
              'observed-coverage': '本期现金结余观察覆盖，不代表未来能维持'}
    for key, row in result['coverage'].items():
        label = '宣告分红' if key == 'declaredDividend' else '实际支付分红'
        text += '\n\n%s：现金结余覆盖倍数%s；%s。' % (label, row['cashSurplusCoverage'] or '未知/不适用', states[row['status']])
        if row['profitCoverage']:
            text += ' 同年度利润覆盖为' + row['profitCoverage'] + '倍，利润不等于现金。'
    text += '\n\n## 来源与缺口\n\n'
    labels = dict(operatingCashFlow='经营现金流', capitalExpenditure='资本开支', profit='利润', oneOffProfit='一次性收益', declaredDividend='宣告分红', paidDividend='实际支付分红')
    for key in labels:
        fact = spec['facts'].get(key)
        text += labels[key] + '：' + (fact['source'] + '；教学值，未核验原文。报告期' + fact['period'] + '，版本' + fact['statementVersion'] + '，范围' + fact['scope'] if fact else '缺失') + '\n\n'
        if fact and key in ('declaredDividend', 'paidDividend'):
            text += '分红所属年度：' + (fact.get('attributablePeriod') or '未知') + '；该行金额期间：' + fact['period'] + '。\n\n'
    text += '\n\n'.join(result['limitations']) + '\n\n不构成投资建议。'
    out.mkdir(parents=True)
    for name, content in [('input.json', json.dumps(spec, ensure_ascii=False, indent=2)),
                          ('result.json', json.dumps(result, ensure_ascii=False, indent=2)), ('报告.md', text),
                          ('报告.html', '<!doctype html><meta charset="utf-8"><title>分红观察</title><main style="max-width:900px;margin:40px auto;font:18px/1.8 sans-serif;white-space:pre-wrap">' + html.escape(text) + '</main>')]:
        (out / name).write_text(content, encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('重复JSON字段：' + key)
            result[key] = value
        return result
    def reject_constant(value):
        raise ValueError('JSON不支持非有限数字：' + value)
    publish(json.loads(args.input.read_text('utf-8-sig'), object_pairs_hook=unique_fields,
                       parse_constant=reject_constant), args.out_dir)
