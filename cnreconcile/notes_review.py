# SPDX-License-Identifier: MIT
"""Explicit disclosure-note cash/debt bridge, never infer capitalized interest."""
from .engine import UNITS, validate_fact, verify_pdf_quote
from .review_io import cli, day


def review(spec):
    if spec.get('inputSchema') != 'financial-notes/1':
        raise ValueError('输入须为 financial-notes/1')
    cutoff = day(spec['asOfDate']).isoformat()
    facts = {}; meta = {}; dimensions = None
    fields = {'cash','restrictedCash','shortDebt','ebit','interestExpense','capitalizedInterest'}
    for row in spec['facts']:
        metric = row['metric']
        if metric not in fields or metric in facts:
            raise ValueError('附注字段不支持或重复')
        key = tuple(row[k] for k in ('entity','period','scope','currency','statementVersion','basis'))
        if not all(isinstance(k,str) and k.strip() for k in key):
            raise ValueError('附注须明确主体、期间、范围、币种、版本和累计/单季')
        if dimensions is not None and key != dimensions:
            raise ValueError('附注口径不同，不能直接拼接金额')
        dimensions = key
        if row['value'] is None:
            validate_fact(dict(row, value=0), cutoff)
            facts[metric] = None
            meta[metric] = dict(row, pageEvidenceStatus='evidence-missing')
            continue
        value, _ = validate_fact(row, cutoff)
        if metric != 'ebit' and value < 0:
            raise ValueError('现金、债务或利息金额不能为负')
        if not row.get('evidence'):
            raise ValueError('已知数须有附注定位及短引句')
        state = verify_pdf_quote(row['evidence'])
        facts[metric] = value
        meta[metric] = dict(row, pageEvidenceStatus=state)
    def get(k): return facts.get(k)
    cash, restricted, debt = get('cash'), get('restrictedCash'), get('shortDebt')
    if cash is not None and restricted is not None and restricted > cash:
        raise ValueError('受限现金不能大于同口径货币资金')
    available = cash-restricted if cash is not None and restricted is not None else None
    coverage = available/debt if available is not None and debt is not None and debt>0 else None
    exp, cap, ebit = get('interestExpense'), get('capitalizedInterest'), get('ebit')
    total = exp+cap if exp is not None and cap is not None else None
    interest_coverage = ebit/total if ebit is not None and total is not None and total>0 else None
    values = {'availableCash':str(available) if available is not None else None, 'shortDebtCoverage':str(coverage) if coverage is not None else None, 'disclosedTotalInterest':str(total) if total is not None else None, 'ebitToDisclosedTotalInterest':str(interest_coverage) if interest_coverage is not None else None}
    missing = sorted(fields-set(facts) | {k for k,v in facts.items() if v is None})
    original_checks = sum(r['pageEvidenceStatus']=='quote-found-on-page' for r in meta.values())
    return {'methodVersion':'financial-notes/1', 'status':'partial' if missing else 'ready-for-review', 'sourceVerified':False, 'conclusion':'先扣除明确披露的受限资金，再看短债覆盖；利息费用与资本化利息仅按同口径披露合计，不能把现金流量表的分红及付息混合项当成真实付息。', 'values':values, 'facts':meta, 'missing':missing, 'humanRows':[['可用现金（基础币种金额）',values['availableCash'] or '未知'],['可用现金/短债',values['shortDebtCoverage'] or '未知或分母为零'],['EBIT/披露利息总额',values['ebitToDisclosedTotalInterest'] or '未知或分母为零'],['原页短引句核对',f'{original_checks} 项找到短引句；其余原页未核或证据不足，详见底稿'],['缺失字段','、'.join(missing) or '所需字段已声明，仍需核原文']], 'limitations':['本轮是按声明附注的算术桥接，不证明现金可即时变现或债务口径完整','没有直接披露的资本化利息不通过现金付息减利润表利息倒推','原页找到短引句也不证明金额提取正确；不将异常判为造假、违约或买卖建议','缺字段不填零；不把债券余额当成主体全部有息债务']}


if __name__ == '__main__':
    raise SystemExit(cli({'review':review}, '现金与付息附注核对'))
