def markdown(r):
    conflicts=sum(x['status']=='value-conflict' for x in r['results']);incomparable=sum(x['status']=='not-comparable' for x in r['results'])
    text=f'# 财报字段核对\n\n本次有{conflicts}项数值差异，{incomparable}项口径不同、暂不能直接比较。数值吻合和原文核验是两件事，不能合并成一个“通过”。\n\n'
    for row in r['results']:
        text+=f"## {row['metric']}｜{row['period']}\n\n{row['conclusion']}。\n\n"
        if row['conflictingDimensions']:text+='不同口径：'+', '.join(row['conflictingDimensions'])+'。\n'
        else:text+=f"换算基础金额后，差额为{row['difference']}，声明精度允许的舍入差为{row['roundingTolerance']}。\n"
        states={'quote-found-on-page':'指定PDF物理页找到引句，但未证明数值提取正确','declared-not-page-verified':'引句和页码仅为声明，未核本地原页','pdf-component-missing':'缺PDF读取组件，未执行原页核对','quote-not-found':'指定物理页未找到引句','evidence-missing':'未提供页码引句'}
        text+='原文状态：'+states[row['pageEvidenceStatus']]+'。\n'
        text+='来源：'+row['reportedSource']+'；原文：'+row['originalSource']+'。\n\n'
    return text+'## 使用限制\n\n'+'\n'.join('- '+x for x in r['limitations'])+'\n'
