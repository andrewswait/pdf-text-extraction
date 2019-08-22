import os
import unittest
import time
from lxml import etree
from extration.tests import TEST_DATA_DIR
from extration.pdf_to_xml.converter.converter_poppler import Converter, TextBox
from extration.pdf_to_xml.document import convert_to_html, convert_to_xml


class TestConverter(unittest.TestCase):
    def test_process_pdf_to_html(self):
        self.folder = os.path.join(TEST_DATA_DIR, 'pdftohtml')
        for filename in [item for item in os.listdir(self.folder) if item.endswith('_pdftohtml.xml')]:
            # filename = 'NDA new_1.4_pdf2xml.xml'
            print(filename)
            input_filename = os.path.join(self.folder, filename)
            document = Converter(True).process_pdf2xml(input_filename)
            convert_to_html(document, os.path.join(self.folder, '{}.html'.format(filename[:-4])))
            # break

    def test_process_pdf_to_xml(self):
        self.folder = os.path.join(TEST_DATA_DIR, 'pdftohtml')
        for filename in [item for item in os.listdir(self.folder) if item.endswith('_pdftohtml.xml')]:
            # filename = '(smw-1-tandcs) ISM Agt final.pdf'
            t0 = time.time()
            input_filename = os.path.join(self.folder, filename)
            document = Converter(True).process_pdf2xml(input_filename)
            xml = convert_to_xml(document, os.path.join(self.folder, '{}.xml'.format(filename.replace('_pdftohtml.xml', ''))))
            print('Processed {0}: {1:.3f} seconds'.format(filename, (time.time() - t0)))
            self.assertIsNotNone(etree.fromstring(xml[38:]))
            # break

    def test_broken_words(self):
        filename = os.path.join(TEST_DATA_DIR, 'pdftohtml', 'snippet_1.xml')
        document = Converter(False).process_pdf2xml(filename)
        self.assertEqual(document[0][0].text, 'E', 'Word is misaligned')
        self.assertEqual(document[0][1].text, 'XECUTION ', 'Word is misaligned')

    def test_control_characters(self):
        filename = os.path.join(TEST_DATA_DIR, 'pdftohtml', 'snippet_2.xml')
        document = Converter(False).process_pdf2xml(filename)
        self.assertEqual(document[0][0].text, '0LGGOH0DUNHW&amp;UHGLW)XQG639//&amp;', 'Control chars not removed')
        self.assertEqual(len([b for b in document[0]._boxes if isinstance(b, TextBox)]), 6, 'length is not correct')

    def test_fix_page_width(self):
        filename = os.path.join(TEST_DATA_DIR, 'pdftohtml', 'snippet_3.xml')
        Converter(False)._output_folder = os.path.splitext(filename)[0]
        document = Converter(False).process_pdf2xml(filename)
        self.assertTrue([b.text for b in document._pages[0]._boxes if isinstance(b, TextBox) and b.text == 'occupier thereof and in the event of any rates taxes assessments '],
                        'text is missing')
        self.assertEqual(document._pages[0].width, 952, 'Width is not correct')


if __name__ == '__main__':
    unittest.main()
