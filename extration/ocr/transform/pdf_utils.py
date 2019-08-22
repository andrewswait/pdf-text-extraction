import os
import glob
import io
import time
import logging
import subprocess
from extration.ocr.data import TESS_DATA_DIR, DICTIONARIES_DIR
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from extration.ocr.transform.file_utils import get_filename_from_path

LOGGER = logging.getLogger(__name__)


def split_pages(filename, out_dir, resolution=300, converter='ghostscript'):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    t0 = time.time()
    clean_name = get_filename_from_path(filename)
    if converter == 'PyPDF2':
        with open(filename, 'rb') as infile:
            reader = PdfFileReader(infile)
            for i in range(reader.getNumPages()):
                writer = PdfFileWriter()
                writer.addPage(reader.getPage(i))

                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                img = Image.open(file=pdf_bytes, resolution=resolution)
                img.convert('png')
                img.save(filename=os.path.join(out_dir, '{}-{}.tiff'.format(clean_name, i.zfill(4))))
    elif converter == 'ghostscript':
        command = 'gswin64c' if os.name == 'nt' else 'gs'
        arguments = [command,
                     '-q',
                     '-dBATCH',
                     '-dNOPAUSE',
                     '-dInterpolateControl=1',
                     '-sOutputFile={}-%04d.tiff'.format(os.path.join(out_dir, 'page')),
                     '-sDEVICE=tiffgray',
                     '-r{}'.format(resolution),
                     filename]

        sp = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sp.wait()
        if sp.returncode is not None and sp.returncode != 0:
            _, stderr = sp.communicate()
            if stderr:
                raise Exception('Ghostscript error:{}', format(stderr))
    else:
        raise Exception('Wrong choice for input argument "pdf_to_xml"')

    LOGGER.info('Split pdf pages finished ({:.3f} sec)'.format((time.time() - t0)))
    return glob.glob(os.path.join(out_dir, '*.tiff'))


def merge_pages(directory, out_filename):
    t0 = time.time()

    merger = PdfFileMerger()
    for filename in sorted([file for file in glob.glob(os.path.join(directory, 'page-*.pdf'))]):
        with open(os.path.join(directory, filename), 'rb') as f:
            merger.append(PdfFileReader(f))

    merger.write(out_filename)
    LOGGER.info('Merge pdf pages finished ({:.3f} sec)'.format((time.time() - t0)))


def decrease_size(filename, converter='ghostscript'):
    t0 = time.time()
    out_filename = filename.replace('.pdf', '_small.pdf')
    if converter == 'ghostscript':
        command = 'gswin64c' if os.name == 'nt' else 'gs'
        arguments = [command,
                     '-dBATCH',
                     '-dNOPAUSE',
                     '-dQUIET',
                     '-sOutputFile={}'.format(out_filename),
                     '-sDEVICE=pdfwrite',
                     '-dCompatibilityLevel=1.7',
                     '-dPDFSETTINGS=/ebook',
                     '-sPAPERSIZE=a4',
                     '-dFIXEDMEDIA',
                     filename]

        sp = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sp.wait()
        if sp.returncode is not None and sp.returncode != 0:
            stdout, stderr = sp.communicate()
            if stderr:
                raise Exception('Ghostscript error:{}', format(stderr))
        try:
            os.remove(filename)
            os.rename(out_filename, filename)
        except:
            raise Exception('Ghostscript error: Rename final PDF failed')
    else:
        raise Exception('Wrong choice for input argument "pdf_to_xml"')

    LOGGER.info('Decrease pdf size finished ({:.3f} sec)'.format((time.time() - t0)))


def run_tesseract_3(filename):
    t0 = time.time()
    arguments = ['tesseract',
                 '--user-patterns', os.path.join(DICTIONARIES_DIR, 'eng.user-patterns'),  # Define list of usual patterns
                 filename,
                 filename.replace('_clean.tiff', ''),
                 'pdf']
    sp = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    if sp.returncode is not None and sp.returncode != 0:
        stdout, stderr = sp.communicate()
        if stderr:
            print('Tesseract error:{}', format(stderr))

    LOGGER.info('Tesseract OCR finished ({:.3f} sec)'.format((time.time() - t0)))
    return filename.replace('_clean.tiff', '.pdf')


def run_tesseract_4(filename):
    # Install Tesseract4
    # ====================
    # sudo add-apt-repository ppa:alex-p/tesseract-ocr
    # sudo apt-get update
    # sudo apt install tesseract-ocr

    t0 = time.time()
    arguments = ['tesseract',
                 '--tessdata-dir', TESS_DATA_DIR,  # Define LSTM models path
                 #'--user-words', os.path.join(DICTIONARIES_DIR, 'eng.user-words'),  # Define list of usual words
                 '--user-patterns', os.path.join(DICTIONARIES_DIR, 'eng.user-patterns'),  # Define list of usual patterns
                 '-l', 'eng',  # Define language
                 '--psm', '1',  # Automatic segmentation with OSD.
                 '--oem', '1',  # LSTM engine only
                 filename,
                 filename.replace('_clean.tiff', ''),
                 'pdf']
    sp = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    if sp.returncode is not None and sp.returncode != 0:
        stdout, stderr = sp.communicate()
        print(stdout)
        if stderr:
            print('Tesseract error:{}', format(stderr))

    LOGGER.info('Tesseract OCR finished ({:.3f} sec)'.format((time.time() - t0)))
    return filename.replace('_clean.tiff', '.pdf')

