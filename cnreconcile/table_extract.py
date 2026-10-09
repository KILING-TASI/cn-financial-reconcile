"""Explicit local table-cell extraction; not an arbitrary financial-report parser."""
from pathlib import Path
import hashlib,datetime,re
from urllib.parse import urlparse
from .engine import decimal,validate_fact,verify_pdf_quote

def positive(value,label):
    if isinstance(value,bool) or not isinstance(value,int) or value<1:raise ValueError(label+'须为从1起的正整数')
    return value-1

def extract_amount(spec):
    import pdfplumber
    path=Path(spec['pdfPath']);context=dict(spec['context']);cutoff=spec['asOf']
    if datetime.date.fromisoformat(cutoff).isoformat()!=cutoff:raise ValueError('截止日无效')
    if not path.is_file() or path.stat().st_size>64*1024*1024:raise ValueError('本地PDF缺失或过大')
    source=urlparse(context.get('source',''))
    if source.scheme!='https' or not source.hostname:raise ValueError('须保留原文HTTPS来源')
    selector=spec['selector'];page_index=positive(selector['physicalPage'],'页码');table_index=positive(selector['tableIndex'],'表索引');row_index=positive(selector['rowIndex'],'行索引');column_index=positive(selector['columnIndex'],'列索引');header_index=positive(selector['headerRowIndex'],'表头行')
    normalize=lambda value:re.sub(r'\s+','',value or '')
    for key in ('rowLabel','columnLabel'):
        if not isinstance(selector.get(key),str) or not selector[key].strip():raise ValueError('行列标签缺失')
    with pdfplumber.open(path) as doc:
        if page_index>=len(doc.pages):raise ValueError('页码超界')
        identity=normalize(''.join(p.extract_text() or '' for p in doc.pages[:3]))
        if not isinstance(context.get('entity'),str) or normalize(context['entity']) not in identity:raise ValueError('主体文字未在文档首页找到')
        tables=doc.pages[page_index].find_tables()
        if table_index>=len(tables):raise ValueError('表格索引超界')
        table=tables[table_index];rows=table.extract()
        if row_index>=len(rows) or header_index>=len(rows) or column_index>=len(rows[row_index]) or column_index>=len(rows[header_index]):raise ValueError('行列位置超界')
        row=rows[row_index];header=rows[header_index]
        if normalize(selector['rowLabel']) not in [normalize(cell) for cell in row]:raise ValueError('指定行标签不匹配')
        if normalize(header[column_index])!=normalize(selector['columnLabel']):raise ValueError('指定比较列标签不匹配')
        if any(token in normalize(selector['rowLabel']) for token in ('每股','元/股','%','％','比例','增长率')):raise ValueError('首版只提取金额，不将每股或比率视为金额')
        row_units=set(re.findall(r'亿元|万元|千元|元',normalize(selector['rowLabel'])))
        if len(row_units)!=1 or context.get('unit') not in row_units:raise ValueError('声明金额单位须与原行明示单位完全一致，不能将千元当元')
        if any(token in normalize(selector['columnLabel']) for token in ('%','％','比率','增长','增减')):raise ValueError('变化率列不作为金额列')
        raw=row[column_index]
        if not isinstance(raw,str) or not raw.strip():raise ValueError('指定金额单元格缺失')
        value=decimal(normalize(raw).replace(',',''))
        fact=dict(context,value=str(value));validate_fact(fact,cutoff)
        locator={key:selector[key] for key in ('physicalPage','tableIndex','rowIndex','columnIndex','headerRowIndex','rowLabel','columnLabel')}
        locator.update(rawCell=raw,rawRow=row,rawHeader=header,bbox=list(table.bbox),coordinateSystem='PDF points, top-left origin',sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return {'toolVersion':'cnreconcile-table-0.1.dev1','inputSchema':'explicit-table-cell-v1','rulesVersion':'row-column-unit-1','fact':fact,'tableEvidence':locator,'status':'explicit-cell-extracted','limitations':['主体/期间/合并范围/币种/累计口径仍依赖输入声明，未自动认证','表格坐标与单元格提取不等于审计结论，不自动处理任意PDF或扫描件']}

def validate_versions(documents,relations,as_of):
    if datetime.date.fromisoformat(as_of).isoformat()!=as_of:raise ValueError('版本核对截止日无效')
    if not isinstance(documents,list) or not documents or not isinstance(relations,list):raise ValueError('文档和版本关系须为列表')
    docs={}
    for doc in documents:
        key=doc['id']
        if not isinstance(key,str) or not key.strip() or key in docs:raise ValueError('文档标识缺失或重复')
        if datetime.date.fromisoformat(doc['publishedAt']).isoformat()!=doc['publishedAt'] or doc['publishedAt']>as_of:raise ValueError('版本披露日期无效')
        if not re.fullmatch('[0-9a-f]{64}',doc.get('sha256','')) or not doc.get('entity') or not doc.get('version'):raise ValueError('文档版本身份缺失')
        docs[key]=doc
    edges=[]
    for relation in relations:
        before,after=relation['from'],relation['to']
        if before not in docs or after not in docs or before==after or relation['type'] not in ('correction','restatement'):raise ValueError('版本关系无效')
        if docs[before]['entity']!=docs[after]['entity'] or docs[before]['publishedAt']>docs[after]['publishedAt']:raise ValueError('主体或版本顺序不符')
        fields=relation['fields']
        if not isinstance(fields,list) or not fields or len(set(fields))!=len(fields) or any(not isinstance(x,str) or not x.strip() for x in fields):raise ValueError('需明确受影响字段，不能覆盖整份报告')
        evidence=relation.get('evidence')
        if not isinstance(evidence,dict):raise ValueError('更正/重述关系需公告依据')
        status=verify_pdf_quote(evidence)
        edges.append(dict(relation,evidenceStatus=status,priorityDecision='not-automatically-selected'))
    graph={}
    for edge in edges:graph.setdefault(edge['from'],[]).append(edge['to'])
    def walk(key,path):
        if key in path:raise ValueError('版本关系存在循环，不能解释为修订链')
        for next_key in graph.get(key,[]):walk(next_key,path+[key])
    for key in docs:walk(key,[])
    return {'toolVersion':'cnreconcile-table-0.1.dev1','inputSchema':'explicit-version-relations-v1','rulesVersion':'no-automatic-supersession-1','documents':documents,'relations':edges,'scope':'explicit version relations; no automatic supersession or audit opinion'}
