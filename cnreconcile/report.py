def markdown(r):
    conflicts=sum(x['status']=='value-conflict' for x in r['results']);incomparable=sum(x['status']=='not-comparable' for x in r['results'])
    text=f'# 财报字段核对\n\n本次有{conflicts}项数值差异，{incomparable}项口径不同、暂不能直接比较。数值吻合和原文核验是两件事，不能合并成一个“通过”。\n\n'
    for row in r['results']:
        text+=f"## {row['metric']}｜{row['period']}\n\n{row['conclusion']}。\n\n"
        if row['conflictingDimensions']:text+='不同口径：'+', '.join({'entity':'主体','metric':'字段','period':'期间','scope':'合并范围','currency':'币种','basis':'累计/单季','statementVersion':'原版/修订版本'}.get(x,x) for x in row['conflictingDimensions'])+'。\n'
        else:text+=f"换算基础金额后，差额为{row['difference']}，声明精度允许的舍入差为{row['roundingTolerance']}。\n"
        states={'quote-found-on-page':'指定PDF物理页找到引句，但未证明数值提取正确','declared-not-page-verified':'引句和页码仅为声明，未核本地原页','pdf-component-missing':'缺PDF读取组件，未执行原页核对','quote-not-found':'指定物理页未找到引句','evidence-missing':'未提供页码引句'}
        if row.get('versionComparison')=='not-declared':text+='报表版本未声明，数值相同不表示已经确认同版。\n'
        for hint in row.get('reviewHints',[]):text+='排查提示（非原因结论）：'+hint['message']+'\n'
        text+='原文状态：'+states[row['pageEvidenceStatus']]+'。\n'
        text+='来源：'+row['reportedSource']+'；原文：'+row['originalSource']+'。\n\n'
    return text+'## 使用限制\n\n'+'\n'.join('- '+x for x in r['limitations'])+'\n'


def html_report(r, spec=None):
    from html import escape
    import json,hashlib
    from pathlib import Path
    from .html_controls import table
    body=table(['字段','期间','计算状态','结论'],[[x['metric'],x['period'],{'not-comparable':'口径不可比','matched-within-rounding':'声明精度内吻合','value-conflict':'数值差异'}[x['status']],x['conclusion']] for x in r['results']])
    body=body.replace('<table id="result-table">','<table id="result-table" style="min-width:600px">')
    files=['engine.py','difference_guidance.py','report.py','html_controls.py','__main__.py']
    hashes={f:hashlib.sha256((Path(__file__).parent/f).read_bytes()).hexdigest() for f in files}
    frozen='<details><summary>保存的输入与方法摘要（分享前检查隐私）</summary><pre>'+escape(json.dumps({'input':spec,'methodSha256':hashes},ensure_ascii=False,indent=2,allow_nan=False))+'</pre></details>'
    teaching=all('教学' in row[key] for row in r['results'] for key in ('reportedSource','originalSource'))
    summary='<section aria-label="本次结论"><h1>财报字段核对</h1><p>数值差异 '+str(sum(x['status']=='value-conflict' for x in r['results']))+' 项；口径不可比 '+str(sum(x['status']=='not-comparable' for x in r['results']))+' 项。</p><h2>影响结论的关键缺口</h2><p>金额吻合不等于原页已核实；原页短引句核对不等于数字提取或会计口径正确。差异排查提示是核查方向，不是原因结论。</p></section>'
    summary=summary.replace('<h1>','<p>'+('原创教学样本，非真实研究结论。' if teaching else '按输入声明观察；来源与完整性仍须核对。')+'</p><h1>',1)
    meta='截止日 '+str(r['asOf'])+'；方法 '+r['toolVersion']+' / '+r['inputSchema']+' / '+r['rulesVersion']
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>研究结果</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui,sans-serif;color:#203047}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:10px;text-align:left;overflow-wrap:anywhere}input,select{font:inherit;max-width:100%}</style><body><p>'+escape(meta)+'</p>'+summary+body+'<details><summary>完整说明、未知路径与核查提示</summary><pre>'+escape(markdown(r))+'</pre></details>'+frozen+'<details aria-label="指标怎么读"><summary>指标怎么读、金额怎么核</summary><p>金额差额先按同币种和同单位换算，再检查主体、期间、合并/母公司、累计/单季及修订版本。数值吻合只说明所填精度内一致，不证明原文已核或会计处理正确。</p><p>未知不当作零；比例必须配分母。只有明确完整、同币种基数时才将比例乘基数换成金额。原始结果、方法和资料版本继续保留，新解释不会改写历史冻结报告。</p></details>'+'</body></html>'
