from subprocess import Popen, PIPE
import re
import os
import tempfile
from operator import itemgetter
from math import ceil, floor
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.etree.ElementTree import Element
from extration.pdf_to_xml.document import Document, Page, Block, TextBox, Text
from extration.pdf_to_xml.utilities import create_path
from extration.pdf_to_xml.utilities.character_replace import escape_characters_for_xml
from .utilities import detect_header_footer, detect_blocks, merge_small_blocks, clean_ocr

spaces = re.compile(' +')


class Converter(object):
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._document = None
        self._intermediate_xml = None
        self._output_folder = None

    def process(self, input_file: str, is_ocr=False, no_layout=False):
        if input_file is None:
            raise ValueError('Input filename not provided')
        if self._verbose:
            self._output_folder = os.path.splitext(input_file)[0]
            create_path(self._output_folder)

        with tempfile.TemporaryDirectory() as temp_folder:
            xml_filename = None
            if self._intermediate_xml is None:
                base_name = os.path.basename(os.path.splitext(input_file)[0])
                xml_filename = os.path.join(temp_folder,  '{}_pdf2html.xml'.format(base_name))
                result = Popen(['pdftohtml', '-xml', '-hidden', '-c', input_file, xml_filename], stdout=PIPE, stderr=PIPE)

                result.wait()
                if result.returncode is not None and result.returncode != 0:
                    output, err = result.communicate()
                    raise Exception('Extraction of xml failed: {0} \n {1}'.format(output, err))

            self.process_pdf2xml(xml_filename, is_ocr, no_layout)
        return self._document

    def process_pdf2xml(self, xml_filename: str, is_ocr=False, no_layout=False):
        # Convert initial xml to a document model (and fix some alignment issues)
        self._convert_pdfxml_to_document(xml_filename)

        for page in self._document:
            page.correct_width()
            page.correct_height()
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
                detect_blocks(page, dimension=10 if font_size[0][0] > 10 else 7, output_folder=self._output_folder)
            merge_small_blocks(page, tolerance=50)
        if not no_layout:
            detect_header_footer(self._document)
        if is_ocr:
            clean_ocr(self._document)

        return self._document

    def _convert_pdfxml_to_document(self, xml_filename):
        if xml_filename is not None or self._intermediate_xml is None:
            xml_content = []
            with open(xml_filename, 'r', encoding='utf-8') as f:
                links = re.compile('<a href=".*?">|<\/a>')
                spans = re.compile('<span( class=".*?")*>|<\/span>')
                multi_spaces = re.compile('( )+')
                quotes = re.compile('�')
                control_chars = re.compile(r'[\x00-\x1f\x7f-\x9f]')
                for line in f:
                    line = control_chars.sub('', line)
                    line = links.sub('', spans.sub('', line))
                    line = multi_spaces.sub(' ', quotes.sub('"', line))
                    xml_content.append(line)
            self._intermediate_xml = ''.join(xml_content)
        dom_tree = xml.dom.minidom.parseString(self._intermediate_xml)

        self._document, fonts = Document(), {}
        for page in dom_tree.documentElement.getElementsByTagName('page'):
            current_page = Page(number=int(page.getAttribute('number')),
                                width=int(page.getAttribute('width')),
                                height=int(page.getAttribute('height')))

            for node in [node for node in page.childNodes if node.nodeName == 'fontspec']:
                font_id = int(node.getAttribute('id'))
                font_node = {'size': int(node.getAttribute('size')),
                             'family': node.getAttribute('family'),
                             'color': node.getAttribute('color')}
                fonts[font_id] = font_node

            nodes = sorted([node for node in page.childNodes if node.nodeName == 'text' and node.nodeType == 1],
                           key=lambda x: int(x.getAttribute('top')))

            page_text, previous_top = {}, 0
            for i, node in enumerate(nodes):
                top, left = int(node.getAttribute('top')), int(node.getAttribute('left'))
                width, height = int(node.getAttribute('width')), int(node.getAttribute('height'))

                if abs(ceil(previous_top) - ceil(top)) <= floor(height/2):
                    top = previous_top
                previous_top = top

                text = Converter._get_tag_from_xml_node(node)
                if text is None or not text:
                    continue
                if isinstance(text, list):
                    text = ''.join(text)
                font_details = fonts[int(node.getAttribute('font'))]
                content = Text(text=text, font=font_details['family'], size=font_details['size'])

                page_text[(top, left, width, height)] = content

            # sort the page_text hash by the keys (x0,x1 values of the bbox),
            # which produces a top-down, left-to-right sequence of related columns
            page_text_items = [(k[0], k[1], k, v) for k, v in page_text.items()]
            page_text_items = sorted(page_text_items, key=itemgetter(0, 1))
            sorted_text = [(c, d) for a, b, c, d in page_text_items]

            for k, v in sorted_text:
                current_page.add_box(TextBox(int(k[0]), int(k[1]), int(k[2]), int(k[3]), v))
            self._document.add_page(current_page)

    @staticmethod
    def _get_tag_from_xml_node(xml_node: Element):
        if xml_node.nodeName == '#text':
            if xml_node.data.isspace():
                return None
            return escape_characters_for_xml(xml_node.data)
        else:
            values = []
            if xml_node.hasChildNodes() and len(xml_node.childNodes) == 1\
                    and xml_node.childNodes[0].nodeName == '#text':
                if xml_node.childNodes[0].data.isspace():
                    return None
                return escape_characters_for_xml(xml_node.childNodes[0].data)
            elif xml_node.hasChildNodes():
                for child in xml_node.childNodes:
                    tag = Converter._get_tag_from_xml_node(child)
                    if tag is not None and hasattr(child, 'tagName'):
                        if isinstance(tag, list):
                            values.append('<{}>{}</{}>'.format(child.tagName, ' '.join(tag), child.tagName))
                        else:
                            values.append('<{}>{}</{}>'.format(child.tagName, tag, child.tagName))
                    elif tag is not None and not hasattr(child, 'tagName'):
                        values.append(tag)
            return values
