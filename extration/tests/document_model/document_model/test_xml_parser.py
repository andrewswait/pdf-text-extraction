import os
import logging
import unittest
from annual_reports.data import TEST_DATA_DIR
from annual_reports.document_model.parsers import XmlParser
from annual_reports.document_model.document import Interval

LOGGER = logging.getLogger(__name__)


class TestParsers(unittest.TestCase):
    def setUp(self):
        self._xml_parser = XmlParser()
        self._folder = os.path.join(TEST_DATA_DIR, 'parsers', 'xml_1')

    def test_create(self):
        assert isinstance(self._xml_parser, XmlParser)

    def test_parse_xml_quotes(self):
        input_file = os.path.join(self._folder, 'multiple_quotes.xml')
        document = self._xml_parser.read_file(input_file)
        self.assertEqual(len(document.tokens), 150, 'Contract not parsed successfully')

    def test_raw_xml_1(self):
        input_file = os.path.join(self._folder, 'parser_test_1.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(71, 71))
        self.assertEqual(document.xml[clause.start:clause.end],
                         '1</emphasis>.2', 'Raw xml indices are not correct')

    def test_raw_xml_2(self):
        input_file = os.path.join(self._folder, 'parser_test_2.xml')

        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        payment_clause = document.get_content_interval(Interval(125, 127))

        self.assertEqual(document.xml[payment_clause.start:payment_clause.end],
                         'Non</emphasis>-<emphasis role="bold">payment', 'Raw xml indices are not correct')

    def test_raw_xml_3(self):
        input_file = os.path.join(self._folder, 'parser_test_3.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(46, 46))
        self.assertEqual(document.xml[clause.start:clause.end], 'uonsag')

    def test_raw_xml_4(self):
        input_file = os.path.join(self._folder, 'parser_test_4.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(15366, 15373))
        self.assertEqual(document.xml[clause.start:clause.end], 'Section 4.03. Name Change or Relocation</emphasis>.')

    def test_raw_xml_5(self):
        input_file = os.path.join(self._folder, 'parser_test_5.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(39, 43))
        self.assertEqual(document.xml[clause.start:clause.end], '&quot;Class A-1 Notes&quot;')

    def test_raw_xml_6(self):
        """Actually a retokenize test"""
        input_file = os.path.join(self._folder, 'parser_test_6.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        self.assertEqual(document.tokens[28].text, '’')

    def test_raw_xml_7(self):
        input_file = os.path.join(self._folder, 'parser_test_7.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(11, 13))
        self.assertEqual(document.xml[clause.start:clause.end],
                         '&quot;</box><box top="834" left="22" height="13" width="549" font_size="9" font-family="Times"> &quot;')

    def test_raw_xml_8(self):
        input_file = os.path.join(self._folder, 'parser_test_8.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(14, 14))
        self.assertEqual(document.xml[clause.start:clause.end],
                         'S</emphasis></emphasis></box><box top="880" left="557" height="9" width="6" font_size="3" font-family="Times"><emphasis role="italics"><emphasis role="bold">.',
                         'Tokens not found')

    def test_raw_xml_9(self):
        input_file = os.path.join(self._folder, 'parser_test_9.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(13, 13))
        self.assertEqual(document.xml[clause.start:clause.end], 'Postcode', 'Tokens not found')

    def test_raw_xml_10(self):
        input_file = os.path.join(self._folder, 'parser_test_10.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(199, 201))
        self.assertEqual(document.xml[clause.start:clause.end], '&quot;Servicer&quot;', 'Tokens not found')

    def test_raw_xml_11(self):
        """ Long tokens"""
        input_file = os.path.join(self._folder, 'parser_test_11.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(241, 269))
        self.assertEqual(document.xml[clause.start:clause.end], '_____________________________', 'Tokens not found')

    def test_raw_xml_12(self):
        input_file = os.path.join(self._folder, 'parser_test_12.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(17, 17))
        self.assertEqual(document.xml[clause.start:clause.end], 'Transition', 'Tokens not found')

    def test_raw_xml_13(self):
        input_file = os.path.join(self._folder, 'parser_test_13.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(8, 9))
        self.assertEqual(document.xml[clause.start:clause.end], '&quot;_', 'Tokens not found')

    def test_raw_xml_14(self):
        input_file = os.path.join(self._folder, 'parser_test_14.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(76, 78))
        self.assertEqual(document.xml[clause.start:clause.end], '&quot;Parties&quot;', 'Tokens not found')

    def test_raw_xml_15(self):
        """ Tails needs spaces as well"""
        input_file = os.path.join(self._folder, 'parser_test_15.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(36, 36))
        self.assertEqual(document.xml[clause.start:clause.end], 'means', 'Tokens not found')

    def test_raw_xml_16(self):
        input_file = os.path.join(self._folder, 'parser_test_16.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(81, 81))
        self.assertEqual(document.xml[clause.start:clause.end], 'is', 'Tokens not found')
        clause = document.get_content_interval(Interval(105, 105))
        self.assertEqual(document.xml[clause.start:clause.end], '&quot;', 'Tokens not found')

    def test_raw_xml_17(self):
        input_file = os.path.join(self._folder, 'parser_test_17.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(6, 8))
        self.assertEqual(document.xml[clause.start:clause.end], '8th February 2008', 'Tokens not found')

    def test_raw_xml_18(self):
        input_file = os.path.join(self._folder, 'parser_test_18.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        clause = document.get_content_interval(Interval(1997, 1997))
        self.assertEqual(document.xml[clause.start:clause.end], 'Premises', 'Tokens not found')
        clause = document.get_content_interval(Interval(3640, 3640))
        self.assertEqual(document.xml[clause.start:clause.end], '2.2.2', 'Tokens not found')

    def test_parse_generate(self):
        input_file = os.path.join(self._folder, 'back_n_forth.xml')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        document = self._xml_parser.read(content)
        xml_bytes = self._xml_parser.write(document)
        compare = '<content><page height="1263" number="1" width="892"><block left="22" top="864"><box font-family="Times" font_size="9" height="13" left="22" top="864" width="229"><emphasis role="bold">7. TERM AND TERMINATION</emphasis></box><box font-family="Times" font_size="9" height="13" left="22" top="877" width="4"> </box><box font-family="Times" font_size="9" height="13" left="63" top="890" width="803"><emphasis role="bold">7.1 </emphasis> Tail of emphasis</box></block><block left="22" top="903"><box font-family="Times" font_size="9" height="13" left="22" top="903" width="229">for one (1) year after the Effective Date.</box><box font-family="Times" font_size="9" height="13" left="63" top="929" width="796"><emphasis role="bold">7.2 </emphasis> Between emphasis <emphasis role="bold">inside emphasis</emphasis> final</box></block><block left="22" top="942"><box font-family="Times" font_size="9" height="13" left="63" top="929" width="796"><emphasis role="bold">7.2 </emphasis> Between emphasis <emphasis role="bold"><emphasis role="italics">inside</emphasis></emphasis> final</box><box font-family="Times" font_size="9" height="13" left="63" top="1032" width="770">Directly in a box</box></block><block left="22" top="1045"><box font-family="Times" font_size="9" height="13" left="22" top="1045" width="156">One box</box>Inside boxes<box font-family="Times" font_size="9" height="13" left="63" top="1058" width="4">Another box</box></block><block left="22" top="1045"><box font-family="Times" font_size="9" height="13" left="22" top="1045" width="156">One box</box>Inside boxes<box font-family="Times" font_size="9" height="13" left="63" top="929" width="796"><emphasis role="bold"> Another box </emphasis> Between emphasis <emphasis role="bold">inside emphasis</emphasis> final</box></block></page></content>'
        self.assertEqual(xml_bytes.decode('utf-8')[38:], compare, 'Donnot match')


if __name__ == '__main__':
    unittest.main()
