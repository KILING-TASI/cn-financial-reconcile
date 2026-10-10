"""Read-only declared-field preflight; never opens PDF or computes reconciliation."""
from .engine import validate_fact, UNITS
from datetime import date

def inspect(spec):
    errors=[];warnings=[]
    def issue(path,message):errors.append(dict(fieldPath=path,message=message))
    if not isinstance(spec,dict):
        issue('$','输入须为对象');spec={}
    if spec.get('inputSchema') not in (None,'cnreconcile-pairs-v1'):issue('inputSchema','仅支持cnreconcile-pairs-v1')
    cutoff=spec.get('asOf')
    try:
        if not isinstance(cutoff,str) or date.fromisoformat(cutoff).isoformat()!=cutoff:raise ValueError()
    except (ValueError,TypeError):issue('asOf','须为YYYY-MM-DD');cutoff=None
    rows=spec.get('pairs')
    if not isinstance(rows,list) or not 1<=len(rows)<=10000:issue('pairs','须为1至10000项列表');rows=[]
    for i,row in enumerate(rows):
        prefix=f'pairs[{i}]'
        if not isinstance(row,dict):issue(prefix,'须为对象');continue
        for side in ('reported','extracted'):
            fact=row.get(side);path=prefix+'.'+side
            if not isinstance(fact,dict):issue(path,'须为金额事实对象');continue
            missing=False
            for key in ('entity','metric','period','scope','currency','basis','source','publishedAt','unit','value'):
                if key not in fact:issue(path+'.'+key,'必填字段缺失');missing=True
            if not missing and cutoff:
                try:validate_fact(fact,cutoff)
                except (ValueError,KeyError,TypeError,ArithmeticError) as e:issue(path,str(e))
            version=fact.get('statementVersion')
            if version is not None and (not isinstance(version,str) or not version.strip()):issue(path+'.statementVersion','声明版本须为非空文字')
            if version is None:warnings.append(dict(fieldPath=path+'.statementVersion',message='版本未声明；不能据此确认同版'))
        evidence=row.get('evidence')
        if evidence is not None:
            if not isinstance(evidence,dict):issue(prefix+'.evidence','须为对象')
            else:
                page=evidence.get('page')
                if isinstance(page,bool) or not isinstance(page,int) or page<1:issue(prefix+'.evidence.page','须为正整数物理页码')
                if not isinstance(evidence.get('quote'),str) or not evidence['quote'].strip():issue(prefix+'.evidence.quote','须为非空原文引句')
        if evidence is None or isinstance(evidence,dict):warnings.append(dict(fieldPath=prefix+'.evidence',message='本次未读取PDF、核实引句或检查原件存在性'))
    return dict(type='input-preflight',contract='cnreconcile-pairs-v1',status='invalid' if errors else 'declared-fields-valid',errors=errors,warnings=warnings,networkAccess=False,filesWritten=False,originalVerified=False,calculationPerformed=False,limitations=['仅检查声明字段，不执行金额差异裁决或PDF读取','通过不证明来源、口径声明、提取数字或会计适用性正确'])

CONTRACT={'contract':'cnreconcile-pairs-v1','required':['asOf','pairs'],'pairRequired':['reported','extracted'],'factRequired':['entity','metric','period','scope','currency','basis','source','publishedAt','unit','value'],'units':list(UNITS),'dateFormat':'YYYY-MM-DD','pairLimit':10000,'scope':'契约索引，不是JSON Schema；完整运行仍有后续检查'}


def main():
    import argparse,json
    p=argparse.ArgumentParser(description='本地输入契约索引；不联网、不写文件')
    p.add_argument('--contract',action='store_true',required=True)
    p.parse_args()
    print(json.dumps(CONTRACT,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
