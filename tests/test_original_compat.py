import unittest
from unittest.mock import patch
from cnreconcile.original_compat import verify


class TestOriginalCompat(unittest.TestCase):
    def test_future_schema_not_interpreted_as_original_v1(self):
        for schema in (2,3,None,True):
            with self.subTest(schema=schema),self.assertRaises(ValueError):verify({'schemaVersion':schema})
    def test_credentials_fail_before_pdf_read(self):
        spec=dict(documentPath='not-read.pdf',sourceUrl='https://user:password@example.org/report.pdf',
                  trustedPublisherHosts=['example.org'],sha256='unknown',title='教学报告',issuer='教学公司',
                  reportDate='2025-12-31',publishedAt='2026-03-31',asOf='2026-10-10',publicationExcerpt='2026年3月31日',fields=[{}])
        with patch('cnreconcile.original_compat.Path.read_bytes') as reader:
            with self.assertRaisesRegex(ValueError,'无凭据'):verify(spec)
            reader.assert_not_called()
