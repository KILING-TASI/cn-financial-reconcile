"""Review prompts are hypotheses, not diagnoses of accounting differences."""
VERSION='difference-review-checklist-1'
def guidance(status,dimensions):
    if status=='matched-within-rounding':return []
    names={'entity':'主体','metric':'字段名称（如营业总收入与营业收入）','period':'报告期间','scope':'合并与母公司范围','currency':'币种','basis':'累计与单季','statementVersion':'原版与修订版'}
    checks=[dict(kind='declared-conflict',field=k,message='输入已声明不同的'+names[k]+'；先核对原文，不能直接裁决数值。') for k in dimensions]
    checks.append(dict(kind='review-only',field='checklist',message='排查原文表头和字段名称、单位及舍入精度、主体/期间、合并/母公司、累计/单季、币种和修订版本；涉及含税/不含税时另核对项目定义与注释。'))
    checks.append(dict(kind='not-inferred',field='cause',message='这是核查方向，不是差异原因结论；不按差额大小反推口径，不自动改数或调大容差。'))
    return checks
