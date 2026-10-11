# SPDX-License-Identifier: MIT
"""Incremental cash demand scenarios over a period-comparable dividend baseline."""
from decimal import Decimal
from .dividend_observation import calculate as dividend
from .engine import decimal


def calculate(spec):
    if not isinstance(spec, dict) or spec.get('inputSchema') != 'cash-demand-stress/1':
        raise ValueError('输入须为 cash-demand-stress/1')
    if set(spec) != {'inputSchema', 'baseline', 'scenarios'}:
        raise ValueError('须提供基准及情景，未知字段不能忽略')
    base = dividend(spec['baseline'])
    scenarios = spec['scenarios']
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 30:
        raise ValueError('需1至30个明确情景')
    coverage = base['coverage']['declaredDividend']
    comparable = coverage['status'] in ('observed-coverage', 'nonpositive-denominator-or-cash-surplus')
    amounts = base['amounts']; rows = []; ids = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {'id', 'note', 'operatingCashChange', 'capexChange', 'additionalDemand'}:
            raise ValueError('每个情景须明确增量需求、变动比例和假设依据')
        sid = scenario['id']
        if not isinstance(sid, str) or not sid.strip() or sid in ids or not isinstance(scenario['note'], str) or not scenario['note'].strip():
            raise ValueError('情景ID须唯一，说明不能为空')
        ids.add(sid)
        ocf_change = decimal(scenario['operatingCashChange']); capex_change = decimal(scenario['capexChange'])
        if not -1 <= ocf_change <= 5 or not -1 <= capex_change <= 5:
            raise ValueError('变动比例须在-1至5之间；不是概率')
        demand = scenario['additionalDemand']
        if demand is not None and (isinstance(demand, bool) or decimal(demand) < 0):
            raise ValueError('增量需求须为非负基本货币单位或null未知')
        ocf = None if amounts['operatingCashFlow'] is None else decimal(amounts['operatingCashFlow']) * (1 + ocf_change)
        capex = None if amounts['capitalExpenditure'] is None else decimal(amounts['capitalExpenditure']) * (1 + capex_change)
        surplus = None if ocf is None or capex is None else ocf - capex
        declared = None if amounts['declaredDividend'] is None else decimal(amounts['declaredDividend'])
        margin = None if not comparable or surplus is None or declared is None else surplus - declared
        after = None if margin is None or demand is None else margin - decimal(demand)
        rows.append({'id': sid, 'note': scenario['note'], 'cashSurplusBeforeAdditionalDemand': None if surplus is None else str(surplus),
                     'marginBeforeAdditionalDemand': None if margin is None else str(margin),
                     'incrementalDemandCapacity': None if margin is None else str(max(Decimal(0), margin)),
                     'marginAfterAdditionalDemand': None if after is None else str(after),
                     'status': 'unknown' if after is None else 'shortfall' if after < 0 else 'covered-under-assumptions'})
    unknown = sum(row['status'] == 'unknown' for row in rows)
    shortfall = sum(row['status'] == 'shortfall' for row in rows)
    return {'methodVersion': 'cash-demand-stress/1', 'sampleType': base['sampleType'], 'baselineResult': base, 'currency': base['currency'],
            'status': 'partial' if unknown else 'scenario-calculated', 'scenarios': rows,
            'conclusion': ('教学金额，非公司真实披露。' if base['sampleType'] == 'teaching-only' else '') + f'所列{len(rows)}个假设情景中，{shortfall}个出现现金缺口，{unknown}个保留未知；不计算发生概率或期望收益。',
            'humanRows': [[row['id'], '未知，需补资料或可比期间' if row['status'] == 'unknown' else ('出现缺口：' if row['status'] == 'shortfall' else '假设下余量：') + format(decimal(row['marginAfterAdditionalDemand']), ',.2f') + '基本货币单位（' + base['currency'] + '）'] for row in rows],
            'limitations': ['所有金额使用基本货币单位；0表示明确假设无新增需求，null表示未知',
                            '增量需求仅指基准资本开支之外的新增现金需求，不能重复扣已经进入经营现金流的营运资金',
                            '资金余量不是账户可用余额；期初现金、受限现金、到期债务、收购和融资均未自动取得',
                            '历史年度金额按声明比例做压力变化，不是未来预测；负现金流同比变动须结合符号理解',
                            '覆盖仅限可比年度的声明分红，不能替代实际支付、母公司现金或未来分红安全判断']}


def main():
    import argparse, json, hashlib, html, os, tempfile, shutil
    from pathlib import Path
    from .__main__ import pairs
    from .cli_feedback import utf8_console
    utf8_console()
    parser = argparse.ArgumentParser(description='现金分红增量需求压力测算，不联网、不预测概率')
    parser.add_argument('--input', type=Path, required=True); parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args(); stage = None
    try:
        if args.input.is_symlink() or args.input.stat().st_size > 16 * 1024 * 1024: raise ValueError('输入为链接或过大')
        spec = json.loads(args.input.read_text('utf-8-sig'), object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('非有限JSON')))
        result = calculate(spec); out = args.out_dir.absolute()
        if out.exists() or out.is_symlink(): raise ValueError('输出须新目录，旧结果保留')
        out.parent.mkdir(parents=True, exist_ok=True); stage = Path(tempfile.mkdtemp(prefix='.cash-stress-', dir=out.parent))
        for name, value in [('input.json', spec), ('result.json', result)]: (stage/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), 'utf-8')
        table='<table><tr><th>情景</th><th>分红与额外需求后的余量</th></tr>'+''.join('<tr><td>'+html.escape(a)+'</td><td>'+html.escape(b)+'</td></tr>' for a,b in result['humanRows'])+'</table>'
        limits='<ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in result['limitations'])+'</ul>'
        (stage/'report.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>现金需求压力测算</title><style>body{max-width:960px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;overflow-wrap:anywhere}</style><h1>现金需求压力测算</h1><p>'+html.escape(result['conclusion'])+'</p><p>计算已完成；基准证据状态见下方明细，不代表未来资金安全。</p>'+table+'<h2>适用范围与缺口</h2>'+limits+'<details><summary>完整基准、来源状态与情景结果</summary><pre>'+html.escape(json.dumps(result, ensure_ascii=False, indent=2))+'</pre></details></html>', 'utf-8')
        (stage/'receipt.json').write_text(json.dumps({'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.iterdir()}, 'sourceVerified': False}, indent=2), 'utf-8')
        os.rename(stage, out); print('报告已生成：'+str(out/'report.html')); return 0
    except (ValueError, TypeError, KeyError, OSError, ArithmeticError, ImportError) as error:
        parser.exit(2, '未完成：'+str(error)+'。请核对输入并使用新目录。\n')
    finally:
        if stage is not None and stage.exists():
            if not stage.resolve().is_relative_to(args.out_dir.absolute().parent.resolve()): raise ValueError('临时目录越界')
            shutil.rmtree(stage)


if __name__ == '__main__': raise SystemExit(main())
