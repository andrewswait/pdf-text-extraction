import logging
import time
from extration.ocr.transform.file_utils import get_filename_from_path
from extration.ocr.transform.pdf_utils import decrease_size
from .ocr_file import ocr_file

LOGGER = logging.getLogger(__name__)


def run_image_pipeline(input_filename, temporary_folder, out_type='pdf'):
    t0 = time.time()
    LOGGER.info('Image pipeline started')

    # Run OCR on image
    ocr_filename = '{}_ocr.pdf'.format(get_filename_from_path(input_filename))
    ocr_file(input_filename)

    # Decrease PDF file quality and size
    decrease_size(ocr_filename)

    LOGGER.info('Image pipeline finished ({:.3f} sec)'.format((time.time() - t0)))
    return ocr_filename
