import logging
import unittest
import os
from extration.tests import TEST_DATA_DIR
from extration.ocr.pipeline.scanned_pdf import is_pdf_scanned

LOGGER = logging.getLogger(__name__)


class TestScannedPdf(unittest.TestCase):
    def test_is_pdf_scanned_no(self):
        response = is_pdf_scanned(os.path.join(TEST_DATA_DIR, 'machine_readable.pdf'))
        self.assertFalse(response, 'This pdf is not scanned')

    def test_is_pdf_scanned_no_ocred(self):
        response = is_pdf_scanned(os.path.join(TEST_DATA_DIR, 'scanned_and_ocred.pdf'))
        self.assertFalse(response, 'This pdf is not scanned')

    def test_is_pdf_scanned_yes(self):
        response = is_pdf_scanned(os.path.join(TEST_DATA_DIR, 'scanned.pdf'))
        self.assertTrue(response, 'This pdf is scanned')

    def test_is_pdf_scanned_yes_complex(self):
        response = is_pdf_scanned(os.path.join(TEST_DATA_DIR, 'scanned_with_overlay.pdf'))
        self.assertTrue(response, 'This pdf is scanned')


if __name__ == '__main__':
    unittest.main()
