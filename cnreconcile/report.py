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
    files=['engine.py','difference_guidance.py','report.py','html_controls.py','__main__.py']
    hashes={f:hashlib.sha256((Path(__file__).parent/f).read_bytes()).hexdigest() for f in files}
    frozen='<details><summary>保存的输入与方法摘要（分享前检查隐私）</summary><pre>'+escape(json.dumps({'input':spec,'methodSha256':hashes},ensure_ascii=False,indent=2,allow_nan=False))+'</pre></details>'
    meta='截止日 '+str(r['asOf'])+'；方法 '+r['toolVersion']+' / '+r['inputSchema']+' / '+r['rulesVersion']
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>研究结果</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui,sans-serif;color:#203047}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:10px;text-align:left}input,select{font:inherit;max-width:100%}</style><body><p>'+escape(meta)+'</p><pre>'+escape(markdown(r))+'</pre>'+body+frozen+'</body></html>'
