import unittest
from annual_reports.document_model.parsers import ParserFactory


class TestParserFactory(unittest.TestCase):
    def test_get_parser_text(self):
        parser = ParserFactory.get_parser('Some content here', file_type='txt')
        self.assertTrue('text_parser' in parser.__module__, 'Wrong parser loaded')

    def test_get_parser_fallback(self):
        parser = ParserFactory.get_parser('<?xml version="1.0" encoding="UTF-8"?><content><page number="1" ')
        self.assertTrue('xml_parser_1' in parser.__module__, 'Wrong parser loaded')

    def test_get_parser_v1(self):
        parser = ParserFactory.get_parser('<?xml version="1.0" encoding="UTF-8"?><content '
                                          'version="1.0" extractor="pdftohtml"><page number="1" ')
        self.assertTrue('xml_parser_1' in parser.__module__, 'Wrong parser loaded')

    def test_get_parser_v2(self):
        parser = ParserFactory.get_parser('<?xml version="1.0" encoding="UTF-8"?><content '
                                          'version="2.0" extractor="pdftohtml"><page number="1" ')
        self.assertTrue('xml_parser_2' in parser.__module__, 'Wrong parser loaded')


if __name__ == '__main__':
    unittest.main()
