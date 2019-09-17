import os
import tempfile
from extration.data import DATA_DIR
from extration.ocr import is_pdf_scanned, run_pdf_pipeline
from extration.pdf_to_xml import Converter, convert_to_xml
from extration.document_model import ParserFactory
from extration.document_model import Section, SectionTypes, Interval


if __name__ == '__main__':
    filename = os.path.join(DATA_DIR, 'nda.pdf')
    if is_pdf_scanned(filename):
        with tempfile.TemporaryDirectory() as temp_folder:
            filename = run_pdf_pipeline(filename, temp_folder)

    pdf_model = Converter().process(filename)
    xml_content = convert_to_xml(pdf_model)
    
    document = ParserFactory.get_parser(xml_content).read(xml_content)
    section = Section(document, SectionTypes.EntireDocument, content_idx=Interval(0, len(document.tokens) - 1))

    for i, item in enumerate(section.sentences):
        text = item.text.encode('utf-8').strip()
        print('{}: {}'.format(i, text))