import os
import unittest
import time
from lxml import etree
from extration.tests import TEST_DATA_DIR
from extration.pdf_to_xml.converter.converter_miner import Converter
from extration.pdf_to_xml.document import convert_to_html, convert_to_xml


class TestConverter(unittest.TestCase):
    def test_process_pdf_to_html(self):
        self.folder = os.path.join(TEST_DATA_DIR, 'contracts')
        for filename in [item for item in os.listdir(self.folder) if item.endswith('pdf')]:
            # filename = 'NDA new_1.4.pdf'
            print(filename)
            input_filename = os.path.join(self.folder, filename)
            document = Converter(True).process(input_filename, no_layout=True)
            convert_to_html(document, os.path.join(self.folder, '{}.html'.format(filename[:-4])))
            # break

    def test_process_pdf_to_xml(self):
        self.folder = os.path.join(TEST_DATA_DIR, 'contracts')
        for filename in [item for item in os.listdir(self.folder) if item.endswith('pdf')]:
            # filename = '(smw-1-tandcs) ISM Agt final.pdf'
            t0 = time.time()
            input_filename = os.path.join(self.folder, filename)
            document = Converter(True).process(input_filename, no_layout=True)
            xml = convert_to_xml(document, os.path.join(self.folder, '{}.xml'.format(filename[:-4])), tool='pdfminer')
            print('Processed {0}: {1:.3f} seconds'.format(filename, (time.time() - t0)))
            self.assertIsNotNone(etree.fromstring(xml[38:]))
            # break


if __name__ == '__main__':
    unittest.main()
