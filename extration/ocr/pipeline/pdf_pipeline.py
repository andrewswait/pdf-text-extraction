import logging
import time
import os
from extration.ocr.transform.file_utils import get_filename_from_path, get_file_folder
from extration.ocr.transform.pdf_utils import split_pages, merge_pages, decrease_size
from .ocr_file import ocr_file

LOGGER = logging.getLogger(__name__)


def run_pdf_pipeline(input_filename, temporary_folder):
    t0 = time.time()
    LOGGER.info('Pdf pipeline started')

    # Splitting pdf into pages
    page_files = split_pages(input_filename, temporary_folder)

    for filename in page_files:
        ocr_file(filename)

    # Merge the pages into one pdf
    ocr_filename = '{}_ocr.pdf'.format(os.path.join(get_file_folder(input_filename),
                                                    get_filename_from_path(input_filename)))
    merge_pages(temporary_folder, ocr_filename)

    # Decrease PDF file quality and size
    decrease_size(ocr_filename)

    LOGGER.info('Pdf pipeline finished ({:.3f} sec)'.format((time.time() - t0)))
    return ocr_filename


