import importlib.util,tempfile,unittest
from pathlib import Path
from cnreconcile.engine import verify_pdf_quote

@unittest.skipUnless(importlib.util.find_spec('pypdf'),'optional PDF component not installed')
class Tests(unittest.TestCase):
    def test_quote_presence_absence_and_invalid_page(self):
        from pypdf import PdfWriter
        from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
        with tempfile.TemporaryDirectory() as tmp:
            writer=PdfWriter();page=writer.add_blank_page(width=300,height=200)
            font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
            page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
            content=DecodedStreamObject();content.set_data(b'BT /F1 12 Tf 20 100 Td (Amount 1000) Tj ET')
            page[NameObject('/Contents')]=writer._add_object(content)
            path=Path(tmp)/'teaching.pdf';writer.write(path)
            evidence=dict(pdfPath=str(path),page=1,quote='Amount 1000')
            self.assertEqual(verify_pdf_quote(evidence),'quote-found-on-page')
            self.assertEqual(verify_pdf_quote({**evidence,'quote':'Amount 2000'}),'quote-not-found')
            with self.assertRaises(ValueError):verify_pdf_quote({**evidence,'page':2})
            path.write_text('not a PDF','utf-8')
            with self.assertRaises(ValueError):verify_pdf_quote(evidence)

if __name__=='__main__':unittest.main()
