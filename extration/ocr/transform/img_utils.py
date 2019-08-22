import os
import time
import logging
import subprocess
from ..bin import BIN_DIR

LOGGER = logging.getLogger(__name__)


def clean_image_file(filename):
    """
    http://www.fmwconcepts.com/imagemagick/textcleaner/
    :param filename:
    :return: processed_filename
    """
    t0 = time.time()
    arguments = [os.path.join(BIN_DIR, 'textcleaner'),
                 '-c', '120',        # crop
                 '-g',               # grayscale (binarize)
                 '-e', 'stretch',    # enhance image brightness
                 '-f', '30',         # apply filters to clean background (denoise)
                 '-o', '12',         # number of filters
                 '-u',               # deskew up to 5 degrees (otherwise use deskew tool)
                 '-s', '2',          # sharpen image
                 '-p', '120',        # apply white border (avoid having text close to image borders)
                 filename,
                 filename.replace('.tiff', '_clean.tiff')]
    sp = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    if sp.returncode is not None and sp.returncode != 0:
        _, stderr = sp.communicate()
        if stderr:
          raise Exception('TextCleaner error:{}', format(stderr))

    LOGGER.info('CLEAN Runtime {:.3f} seconds'.format((time.time() - t0)))
    return filename.replace('.tiff', '_clean.tiff')
