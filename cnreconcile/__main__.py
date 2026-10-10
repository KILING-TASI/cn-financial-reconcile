import argparse,json,html,sys
from pathlib import Path
from .engine import reconcile
from .cli_feedback import utf8_console, failure, saved, pdf_unavailable

def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('JSON字段重复：'+k)
  d[k]=v
 return d

def main():
 utf8_console()
 p=argparse.ArgumentParser(description='中国财报字段核对；读取声明资料，不自动联网')
 p.add_argument('input',type=Path);p.add_argument('--format',choices=['json','markdown','html'],default='json');p.add_argument('--out',type=Path)
 p.add_argument("--validate-only","--dry-run",action="store_true",help="仅本地声明字段预检；不联网、不读PDF、不写文件、不计算")
 a=p.parse_args()
 try:
  if a.input.stat().st_size>16*1024*1024:raise ValueError('输入过大')
  spec=json.loads(a.input.read_text('utf-8-sig'),object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('JSON不能含NaN或Infinity')))
  if a.validate_only:
   if a.out or a.format!='json':raise ValueError('预检只向stdout输出JSON，不接受--out或报告格式')
   from .preflight import inspect
   r=inspect(spec);print(json.dumps(r,ensure_ascii=False,indent=2))
   if r['errors']:p.exit(2)
   return
  r=reconcile(spec)
  from .report import markdown
  text=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False) if a.format=='json' else markdown(r)
  if a.format=='html':
   from .report import html_report
   text=html_report(r,spec)
  if a.out:
   a.out.parent.mkdir(parents=True,exist_ok=True)
   with a.out.open('x',encoding='utf-8') as f:f.write(text)
   saved('金额核对报告', a.out.parent, a.out, teaching=all('教学' in row[side].get('source','') for row in spec['pairs'] for side in ('reported','extracted')))
  else:print(text)
  if any(row['pageEvidenceStatus']=='pdf-component-missing' for row in r['results']):pdf_unavailable()
 except (ValueError,KeyError,TypeError,OSError,ArithmeticError,ImportError) as e:p.exit(2,failure(e,a.out))

if __name__=='__main__':main()
