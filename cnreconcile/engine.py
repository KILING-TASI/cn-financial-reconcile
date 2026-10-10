from decimal import Decimal,InvalidOperation
import datetime as dt

UNITS={'元':Decimal(1),'千元':Decimal(1000),'万元':Decimal(10000),'亿元':Decimal(100000000)}


def decimal(value):
    if isinstance(value,bool):raise ValueError('数值不能为布尔值')
    try:result=Decimal(str(value))
    except InvalidOperation as e:raise ValueError('数值无效') from e
    if not result.is_finite():raise ValueError('数值必须有限')
    return result


def validate_fact(fact,cutoff):
    for key in ('entity','metric','period','scope','currency','basis','source'):
        if not isinstance(fact.get(key),str) or not fact[key].strip():raise ValueError('缺少字段：'+key)
    for key in ('period','publishedAt'):
        text=fact.get(key)
        if not isinstance(text,str) or dt.date.fromisoformat(text).isoformat()!=text:raise ValueError('日期格式无效')
    if fact['period']>fact['publishedAt'] or fact['publishedAt']>cutoff:raise ValueError('事实披露晚于截止日或早于报告期')
    unit=fact['unit']
    if unit not in UNITS:raise ValueError('首版只核对明确金额单位，不隐含处理百分数/每股数')
    value=decimal(fact['value'])*UNITS[unit]
    precision=decimal(fact.get('roundingUnit',0))*UNITS[unit]
    if precision<0:raise ValueError('显示舍入单位不能为负')
    return value,precision


def verify_pdf_quote(evidence):
    # Optional local original-page check. No remote downloads or source instructions.
    if not isinstance(evidence.get('page'),int) or isinstance(evidence['page'],bool) or evidence['page']<1:
        raise ValueError('PDF物理页码须为正整数')
    quote=evidence.get('quote')
    if not isinstance(quote,str) or not quote.strip():raise ValueError('原文引句缺失')
    if not evidence.get('pdfPath'):return 'declared-not-page-verified'
    try:from pypdf import PdfReader
    except ImportError:return 'pdf-component-missing'
    from pathlib import Path
    p=Path(evidence['pdfPath'])
    if not p.is_file() or p.stat().st_size>64*1024*1024:raise ValueError('本地PDF缺失或过大')
    try:
        reader=PdfReader(p)
        if evidence['page']>len(reader.pages):raise ValueError('物理页码超出PDF')
        text=reader.pages[evidence['page']-1].extract_text() or ''
    except Exception as error:raise ValueError('PDF无法读取或指定页无效；未完成原页核验') from error
    normalize=lambda s:''.join(s.split())
    return 'quote-found-on-page' if normalize(quote) in normalize(text) else 'quote-not-found'


def reconcile(spec):
    if spec.get('inputSchema') not in (None,'cnreconcile-pairs-v1'):raise ValueError('未知输入schema，须显式转换，不能静默按旧版解释')
    cutoff=spec['asOf']
    if not isinstance(cutoff,str) or dt.date.fromisoformat(cutoff).isoformat()!=cutoff:raise ValueError('截止日无效')
    pairs=spec['pairs']
    if not isinstance(pairs,list) or not pairs or len(pairs)>10000:raise ValueError('需要非空字段配对列表，最多10000项')
    results=[]
    for row in pairs:
        left,right=row['reported'],row['extracted'];lv,lp=validate_fact(left,cutoff);rv,rp=validate_fact(right,cutoff)
        differences=[key for key in ('entity','metric','period','scope','currency','basis') if left[key]!=right[key]]
        for fact in (left,right):
            if fact.get('statementVersion') is not None and (not isinstance(fact['statementVersion'],str) or not fact['statementVersion'].strip()):raise ValueError('声明财报版本须为非空文字')
        version_state='not-declared'
        if left.get('statementVersion') is not None or right.get('statementVersion') is not None:
            version_state='same-declared-version' if left.get('statementVersion')==right.get('statementVersion') else 'different-or-missing-version'
            if version_state=='different-or-missing-version':differences.append('statementVersion')
        # Sum of each displayed value's half-unit rounding allowance.
        tolerance=(lp+rp)/2
        gap=lv-rv
        status='not-comparable' if differences else 'matched-within-rounding' if abs(gap)<=tolerance else 'value-conflict'
        evidence=row.get('evidence');page_status=verify_pdf_quote(evidence) if isinstance(evidence,dict) else 'evidence-missing'
        from .difference_guidance import guidance
        results.append(dict(metric=left['metric'],period=left['period'],status=status,conflictingDimensions=differences,
            versionComparison=version_state,reviewHints=guidance(status,differences),reviewHintsVersion="difference-review-checklist-1",reportedBaseUnits=str(lv),extractedBaseUnits=str(rv),difference=None if differences else str(gap),roundingTolerance=str(tolerance),
            pageEvidenceStatus=page_status,reportedSource=left['source'],originalSource=right['source'],
            conclusion=('数值吻合，但不等于原文已核验' if status=='matched-within-rounding' else '口径不同，不能直接裁决数值' if differences else '数值存在差异，需要回查原文和提取过程')))
    return dict(toolVersion='cn-financial-reconcile-0.2.3',inputSchema='cnreconcile-pairs-v1',rulesVersion='amount-dimensions-2',asOf=cutoff,results=results,limitations=['按声明的主体、期间、合并范围、币种和口径核对；不验证声明本身',
        '原页引句找到不证明数值被正确提取；数值勾稽与原页证据分列','不出审计意见，不将差异直接判为造假','不自动读取全部三表或判断会计法规适用性','未声明财报版本不代表两份原文同版；重述差异不是自动更正判断'])
