import os
from extration.document_model.utilities.file_utilities import write_text_file
from extration.tests import TEST_DATA_DIR
from extration.document_model import Interval
from extration.document_model.parsers import XmlParser


def split_pages(in_folder, out_folder):
    for folder, subs, files in os.walk(in_folder):
        relative_path = os.path.relpath(folder, in_folder) if os.path.relpath(folder, in_folder) != '.' else ''
        for file in files:
            doc = XmlParser.read_file(os.path.join(folder, file))
            for i, page in enumerate(doc.pages):
                page_tokens = [token for token in doc.tokens if page.overlaps(token)]
                if len(page_tokens) > 1:
                    page_range = Interval(page_tokens[0].index, page_tokens[-1].index)
                    page = doc.extract_document_part(page_range)
                    xml_bytes = XmlParser().write(page)
                    write_text_file(os.path.join(out_folder, relative_path, '{}_{}.xml'.format(os.path.splitext(file)[0], i + 1)),
                                    xml_bytes.decode('utf-8'))


if __name__ == '__main__':
    input_folder = os.path.join(TEST_DATA_DIR, 'Annotated - xml')
    out_folder = os.path.join(TEST_DATA_DIR, 'Annotated - xml pages')
    split_pages(input_folder, out_folder)
