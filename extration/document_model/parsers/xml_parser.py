from lxml import etree as etree
from itertools import count
from .base import Parser
from extration.document_model.document import Document, Tag
import logging

logger = logging.getLogger(__name__)


class XmlParser(Parser):
    """ Factory Class for creating Document Objects from XML files """
    def create(self):
        return self

    @classmethod
    def read(cls, content: str):
        """ return a Document using the XML file located at param path """
        content = content.replace('&nbsp;', ' ').replace('\x91', '‘').replace('\x92', '’') \
            .replace('\x93', '“').replace('\x94', '”').replace('\x95', '•').replace('\x96', '-') \
            .replace('\u200b', '').replace('\x97', '—').replace('\x98', '˜').replace('\x99', '™')
        text, tags = cls._parse_xml(content)
        if text == '':
            return Document()
        model = Document(text, tags, content)
        XmlParser._extract_xml_indices(model, content)
        return model

    @staticmethod
    def _parse_xml(xml_content: str):
        """ convert an xml file to plain text and a collection of Tag objects"""
        head = 0
        strings, tags, stack = [], [], []
        integer = count()
        parser = etree.XMLPullParser(['start', 'end'])
        parser.feed(xml_content)

        last_top, line_break, last_text, last_tag = 0, False, None, None
        for event, element in parser.read_events():
            if event == 'start':
                stack.append((head, next(integer)))
                # Figure out where to inject line changes or spaces in the text. i.e when a text is below another
                # or next to it as if in a column.
                # Rule \n: When the previous text_block has a lower top than the current text tag
                # Rule space: When the previous text_block has the same top as the current text tag
                if element.tag in ['page']:
                    last_top = 0
                # Apply the rule
                if element.tag == 'text':
                    if last_top < abs(int(element.attrib['top'])):
                        line_break = True
                        last_top = int(element.attrib['top'])
                    elif last_tag.tag == 'text_block' and last_top == abs(int(element.attrib['top'])) \
                            and element.text is not None and not element.text[0].isspace():
                        element.text = ' ' + element.text
                # Handle the text
                if element.text and element.tag in ['text', 'b', 'i']:
                    if element.text.isspace():
                        strings.append(' ')
                        head += 1
                        continue
                    elif line_break:
                        element.text = '\n' + element.text
                        line_break = False
                    else:
                        # Solve an issue with emphasis elements, where its contents "stick" to those of the next element
                        # because of a lack of a space. So we get 1.1Introduction instead of 1.1 Introduction
                        if last_text is not None and not element.text[0].isspace():
                            if element.tag in ['b', 'i'] and last_text.tag in ['text', 'b', 'i'] \
                                    and not element.text.startswith((' ', ')', ']', '}' '”', '"',
                                                                     '.', ',', '!', ':', ';')) \
                                    and len(strings) > 0 \
                                    and not strings[-1].endswith((' ', '"', '“', '”', '\'', '(', '[', '{')):
                                element.text = ' ' + element.text
                            if element.tag == 'text' and (last_text.text[-1].isdigit() or
                                                          last_text.text[-1] in ['.', ',', ')', ']', '}', '!', ':', ';',
                                                                                 '>', '”', '·', '٪', '%', '$', '£', '€']):
                                element.text = ' ' + element.text

                    strings.append(element.text)
                    head += len(element.text)
                    last_text = element
                last_tag = element
            elif event == 'end':
                # store the order of the tags on a temporary index attribute
                start, index = stack.pop()
                tag = Tag(start, head, element.tag, dict(element.attrib))
                tags.append(tag)
                # store the order of the tags on a temporary index attribute
                tag.index = index
                if not len(stack):  # This is the root element, do not put anything on the tail
                    continue
                if element.tail:
                    if last_text is not None and not element.tail[0].isspace() and element.tag in['b', 'i'] \
                            and not element.tail.startswith((' ', ')', ']', '}' '”', '"', '.', ',', '!', ':', ';'))\
                            and len(strings) > 0 and not strings[-1].endswith((' ',  '"', '“', '”', '\'', '(', '[', '{')):
                        element.tail = ' ' + element.tail
                    strings.append(element.tail)
                    head += len(element.tail)
        # sort the tags in xml document order
        tags = sorted(tags, key=lambda tag: tag.index)
        # remove the temporary index attribute
        map(lambda tag: delattr(tag, 'index'), tags)
        return ''.join(strings), tags
