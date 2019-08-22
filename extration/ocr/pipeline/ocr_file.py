import logging
import os
from extration.ocr.transform.img_utils import clean_image_file
from extration.ocr.transform.pdf_utils import run_tesseract_3, run_tesseract_4

LOGGER = logging.getLogger(__name__)


def ocr_file(filename):
    # Clean page image file (binarize, sharpen, crop, deskew)
    processed_filename = clean_image_file(filename)
    version = int(os.environ['TESSERACT_VERSION']) if 'TESSERACT_VERSION' in os.environ else 4
    if version == 3:
        return run_tesseract_3(processed_filename)
    elif version == 4:
        return run_tesseract_4(processed_filename)
    else:
        raise ValueError('Tesseract version {} is not supported'.format(os.environ['TESSERACT_VERSION']))
