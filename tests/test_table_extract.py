import unittest,tempfile,sys,types,copy
from pathlib import Path
from unittest.mock import patch
from cnreconcile.table_extract import extract_amount,validate_versions
class Tests(unittest.TestCase):
 def spec(self,path):return {'pdfPath':str(path),'asOf':'2026-10-09','context':{'entity':'教学公司','metric':'营业收入','period':'2026-06-30','publishedAt':'2026-08-29','scope':'consolidated','currency':'CNY','basis':'YTD','source':'https://example.org/a.pdf','unit':'千元'},'selector':{'physicalPage':1,'tableIndex':1,'rowIndex':2,'columnIndex':2,'headerRowIndex':1,'rowLabel':'营业收入（千元）','columnLabel':'本报告期'}}
 def fake(self):
  table=types.SimpleNamespace(bbox=(0,0,100,200),extract=lambda:[['','本报告期','上年同期'],['营业收入（千元）','1,234','1,000']])
  page=types.SimpleNamespace(extract_text=lambda:'教学公司',find_tables=lambda:[table])
  class PDF:
   pages=[page]
   def __enter__(self):return self
   def __exit__(self,*args):pass
  return types.SimpleNamespace(open=lambda path:PDF())
 def test_explicit_cell_and_comparison_column_not_overwritten(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'a.pdf';p.write_bytes(b'fake teaching');spec=self.spec(p)
   with patch.dict(sys.modules,{'pdfplumber':self.fake()}):
    current=extract_amount(spec);self.assertEqual(current['fact']['value'],'1234');self.assertEqual(current['tableEvidence']['rowIndex'],2)
    spec['context']['period']='2025-06-30';spec['selector'].update(columnIndex=3,columnLabel='上年同期');prior=extract_amount(spec);self.assertEqual(prior['fact']['period'],'2025-06-30');self.assertEqual(prior['fact']['value'],'1000')
 def test_wrong_row_column_and_future_date_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'a.pdf';p.write_bytes(b'fake teaching')
   for case in ['row','column','future','boolean','unit']:
    spec=self.spec(p)
    if case=='row':spec['selector']['rowLabel']='净利润（千元）'
    if case=='column':spec['selector']['columnLabel']='上年同期'
    if case=='future':spec['context']['publishedAt']='2027-01-01'
    if case=='boolean':spec['selector']['physicalPage']=True
    if case=='unit':spec['context']['unit']='元'
    with patch.dict(sys.modules,{'pdfplumber':self.fake()}):
     with self.assertRaises(ValueError):extract_amount(spec)
 def test_versions_do_not_automatically_replace_old_fact(self):
  documents=[{'id':x,'entity':'教学公司','publishedAt':d,'version':x,'sha256':'a'*64} for x,d in [('old','2025-04-01'),('new','2025-05-01')]]
  relation={'from':'old','to':'new','type':'restatement','fields':['营业收入'],'evidence':{'page':1,'quote':'教学更正依据'}}
  result=validate_versions(documents,[relation],'2026-10-09');self.assertEqual(result['relations'][0]['priorityDecision'],'not-automatically-selected');self.assertEqual(result['relations'][0]['evidenceStatus'],'declared-not-page-verified')
  relation['fields']=[]
  with self.assertRaises(ValueError):validate_versions(documents,[relation],'2026-10-09')
 def test_per_share_row_is_not_money_even_with_yuan_text(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'a.pdf';p.write_bytes(b'fake teaching');spec=self.spec(p);spec['selector']['rowLabel']='基本每股收益（元/股）';spec['context']['unit']='元'
   fake=self.fake();original=fake.open
   def opener(path):
    pdf=original(path);pdf.pages[0].find_tables=lambda:[types.SimpleNamespace(bbox=(0,0,100,200),extract=lambda:[['','本报告期','上年同期'],['基本每股收益（元/股）','3.5','3.0']])];return pdf
   fake.open=opener
   with patch.dict(sys.modules,{'pdfplumber':fake}):
    with self.assertRaises(ValueError):extract_amount(spec)
 def test_same_day_version_cycle_rejected(self):
  documents=[{'id':x,'entity':'教学公司','publishedAt':'2025-05-01','version':x,'sha256':'a'*64} for x in ['a','b']]
  relation=lambda a,b:{'from':a,'to':b,'type':'correction','fields':['营业收入'],'evidence':{'page':1,'quote':'教学更正依据'}}
  with self.assertRaises(ValueError):validate_versions(documents,[relation('a','b'),relation('b','a')],'2026-10-09')
if __name__=='__main__':unittest.main()
