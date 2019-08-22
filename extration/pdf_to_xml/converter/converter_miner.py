import io
import os
from operator import itemgetter
from math import ceil, floor
from collections import Counter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextLineHorizontal, LTChar, LTAnno
from extration.pdf_to_xml.document import Document, Block, ImageBox, TextBox, Text, Page
from extration.pdf_to_xml.utilities import save_image, create_path, font_mapping, round_with_middle
from .utilities import detect_header_footer, detect_blocks, merge_small_blocks, clean_ocr


class Converter(object):
    def __init__(self, verbose=False, caching=False):
        self.resource_manager = PDFResourceManager(caching=caching)
        self._document = None
        self._verbose = verbose
        self._output_folder = None

    def process(self, input_file: str, is_ocr=False, no_layout=False):
        self.extract_pdf(input_file)
        if self._document is None:
            return None

        for page in self._document:
            font_size = page.get_font_sizes().most_common(1)
            if not font_size:
                continue
            if no_layout:
                page.add_box(Block(top=min((b.top for b in page._boxes)),
                                   left=min((b.left for b in page._boxes)),
                                   width=int(ceil(max((b.right for b in page._boxes)) - min((b.left for b in page._boxes)))),
                                   height=int(ceil(max((b.bottom for b in page._boxes))) - min((b.top for b in page._boxes))))
                             )
            else:
                detect_blocks(page, dimension=10 if font_size[0][0] > 10 else 5, output_folder=self._output_folder)
            merge_small_blocks(page)
        if not no_layout:
            detect_header_footer(self._document)
        if is_ocr:
            clean_ocr(self._document)

        return self._document

    def extract_pdf(self, input_file: str):
        if self._verbose:
            self._output_folder = os.path.splitext(input_file)[0]
            create_path(self._output_folder)

        self._document = Document()
        with io.open(input_file, 'rb') as input_fd:
            device = PDFPageAggregator(self.resource_manager, laparams=LAParams())
            interpreter = PDFPageInterpreter(self.resource_manager, device)

            for i, pdf_page in enumerate(PDFPage.get_pages(input_fd)):
                current_page = Page(number=i + 1,
                                    width=int(pdf_page.mediabox[2]),
                                    height=int(pdf_page.mediabox[3]))

                interpreter.process_page(pdf_page)
                # receive the LTPage object for this page
                layout = device.get_result()
                # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
                self._parse_layout_objects(layout, current_page, self._output_folder)

                self._document.add_page(current_page)

        return self._document

    def _parse_layout_objects(self, layout, page: Page, image_path):
        """Iterate through the list of LT* objects and capture the text or image data contained in each"""
        page_text = {}  # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine) or isinstance(lt_obj, LTTextLineHorizontal):
                self._get_text(page_text, lt_obj)
            elif isinstance(lt_obj, LTImage):
                image_name, file_stream = save_image(lt_obj, 'page_{}_{}_{}'.format(page.number, lt_obj.y0, lt_obj.x0), image_path)
                if image_name:
                    # top = page height - image height - y0, i.e. y0 is the distance from the bottom of the page
                    top = page.height - round(lt_obj.y0) - round(lt_obj.y1 - lt_obj.y0)
                    left = round(lt_obj.x0)
                    width = min(page.width, round(lt_obj.x1 - lt_obj.x0))
                    height = round(lt_obj.y1 - lt_obj.y0)
                    page.add_box(ImageBox(top, left, width, height, image_name, file_stream))

            elif isinstance(lt_obj, LTFigure):
                # LTFigure objects are containers for other LT* objects, so recurse through the children
                self._parse_layout_objects(lt_obj, page, image_path)

        page_text = [(k[0], k[1], k, v) for k, v in page_text.items()]
        page_text = list(sorted(sorted(page_text, key=itemgetter(0)), key=itemgetter(1), reverse=True))
        previous_top, aligned_text = 0, []
        for _, _, k, v in page_text:
            top = k[1]
            if abs(ceil(previous_top) - ceil(top)) <= 2:
                top = previous_top

            # Skip empty text in the beginning of line. Usually these are empty lines
            if top > previous_top and v.text.isspace():
                continue
            previous_top = top
            aligned_text.append((k[0], int(top), (k[0], top, k[2], k[3]), v))

        aligned_text = list(sorted(sorted(aligned_text, key=itemgetter(0)), key=itemgetter(1), reverse=True))
        for _, _, k, v in aligned_text:
            page.add_box(TextBox(int(floor(page.height - k[1])), int(floor(k[0])),
                                 int(ceil(k[2] - k[0]) + 5), int(ceil(k[3] - k[1])), v))

    def _get_text(self, h, block):
        for box in [item for item in block if isinstance(item, LTTextLineHorizontal)]:
            characters = [c for c in box if (isinstance(c, LTChar) or isinstance(c, LTAnno)) and c.get_text() != '\n']
            if len(characters) == 0 or all([True if c.get_text() == ' ' else False for c in characters]):
                continue

            # Get font family
            font = Counter([c.fontname for c in characters if c._text != ' ' and not isinstance(c, LTAnno)]).most_common(1)
            if not font:
                continue
            font = font[0][0]
            font_family = font.split('+')[-1]

            # calculate font size
            char_height = Counter([c.size for c in characters if c.get_text() not in [' ', '.'] and not isinstance(c, LTAnno)]).most_common(1)
            char_height = char_height[0][0] if char_height else 0

            char_width = Counter([floor(c.width) for c in characters if c.get_text() not in [' ', '.'] and not isinstance(c, LTAnno)]).most_common(1)
            char_width = char_width[0][0] if char_width else 0

            font_size = Counter([c.matrix[0] for c in characters if c.get_text() not in [' ', '.'] and not isinstance(c, LTAnno)]).most_common(1)
            font_size = floor(font_size[0][0]) if font_size else 0

            if font_size <= char_width:
                if 6 <= char_height < 14:  # For average to medium fonts the char.size property is the most reliable
                    font_size = round_with_middle(char_height)
                elif char_height < 6:  # Very small fonts is usually a mistake, use width
                    font_size = round(char_width * 2)
                elif 14 <= char_height:  # For large try to correct the height if the 2xwidth is smaller
                    font_size = min(floor(char_width * 2), round_with_middle(char_height))

            text, emphasis, previous = [], [], None
            for c in characters:
                if c.get_text() == ' ' and previous is not None and previous.get_text() == ' ':
                    continue
                if not hasattr(c, 'fontname'):
                    emphasis.append('n')
                elif 'BoldItalic' in c.fontname:
                    emphasis.append('bi')
                elif 'Bold' in c.fontname:
                    emphasis.append('b')
                elif 'Italic' in c.fontname:
                    emphasis.append('i')
                else:
                    emphasis.append('n')
                text.append(c)
                previous = c

            font_family = font_mapping(font_family)
            h[box.bbox] = Text(''.join([c.get_text() for c in text]), font_family, font_size, emphasis)
        return h
