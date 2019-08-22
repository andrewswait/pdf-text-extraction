import logging.config
import os
import click
import sys
from multiprocessing import Pool
from functools import partial
from extration.pdf_to_xml.utilities.file_utilities import get_files_from_path
from extration.pdf_to_xml.converter.converter_poppler import Converter
from extration.pdf_to_xml.document import convert_to_xml

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option('--path', help='The file or folder to process')
@click.option('--out_path', help='Folder in which to store output')
@click.option('--file_type', help='Only process a particular file type')
@click.option('--recursive', is_flag=True, help='Process the folder recursively')
@click.option('--not_overwrite', is_flag=True, help='Don\'t ovewrite output if exists')
def cli(path, out_path, file_type, recursive, not_overwrite):
    if path is None:
        return

    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    if out_path and not os.path.isabs(out_path):
        out_path = os.path.join(os.getcwd(), out_path)

    if os.path.isfile(path):
        process_file(path, os.path.dirname(out_path) if out_path else None, file_type, not not_overwrite)
    elif recursive:
        process_folder_recursive(path, out_path, file_type, not not_overwrite)
    else:
        process_folder(path, out_path, file_type, not not_overwrite)


def process_folder_recursive(path, out_path, file_type, overwrite):
    for folder, subs, files in os.walk(path):
        LOGGER.info('Processing folder (recursive) {}'.format(folder))
        if out_path is None:
            out_path = folder
        relative_path = os.path.relpath(folder, path) if os.path.relpath(folder, path) != '.' else ''
        LOGGER.info('Output folder {}'.format(os.path.join(out_path, relative_path)))
        for file in files:
            process_file(os.path.join(folder, file), os.path.join(out_path, relative_path), file_type, overwrite)


def process_folder(path, out_path, file_type, overwrite, parallel=None):
    files = get_files_from_path(path)
    files = [os.path.join(path, file) for file in files]
    if parallel:
        with Pool(processes=parallel) as pool:
            tmp = partial(process_file, out_path=out_path, file_type=file_type, overwrite=overwrite)
            pool.map(tmp, files)
    else:
        for file in files:
            process_file(file, out_path, file_type, overwrite)


def process_file(filename, out_path=None, file_type=None, overwrite: bool=False):
    if out_path is None:
        out_path = os.path.dirname(filename)

    if file_type is not None and os.path.splitext(os.path.basename(filename))[1][1:].lower() != file_type.lower():
        return

    conv = Converter()
    output_file = os.path.join(out_path, os.path.splitext(os.path.basename(filename))[0] + '.xml')
    LOGGER.info('Convert {}'.format(filename))
    if not overwrite and os.path.isfile(output_file):
        LOGGER.info('File exists, skipping {}'.format(output_file))
        return
    try:
        print(output_file)
        document = conv.process(filename)
        convert_to_xml(document, output_file)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as error:
        LOGGER.error('File {} Failed: {}'.format(output_file, error))


if __name__ == '__main__':
    cli()