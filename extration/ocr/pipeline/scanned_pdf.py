from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextBox, LTTextLine


def is_pdf_scanned(filename):
    with open(filename, 'rb') as file:
        resource_manager = PDFResourceManager()
        device = PDFPageAggregator(resource_manager, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, device)

        content = []
        try:
            for i, pdf_page in enumerate(PDFPage.get_pages(file)):
                interpreter.process_page(pdf_page)
                # receive the LTPage object for this page
                layout = device.get_result()
                page_content = []
                for lt_obj in layout:
                    if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                        page_content.append(lt_obj.get_text())
                content.append(page_content)
        except:
            return True

    if all([len(item) == 0 for item in content]):
        return True
    elif all([len(item) == 1 for item in content]):
        return True
    return False
