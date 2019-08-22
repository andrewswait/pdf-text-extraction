import logging
import importlib
import re
from lxml import etree as etree
from extration.document_model.utilities import escape_characters_for_xml
from extration.document_model.document import Document, Interval

logger = logging.getLogger(__name__)


class ParserFactory:
    @staticmethod
    def get_parser(content: str, file_type='xml'):
        if '<html>' in content[:100]:
            file_type = 'html'
        if file_type == 'txt':
            module = 'extration.document_model.parsers.text_parser'
            class_name = 'TextParser'
        elif file_type == 'html':
            module = 'extration.document_model.parsers.html_parser'
            class_name = 'HtmlParser'
        elif file_type == 'xml':
            class_name = 'XmlParser'
            module = 'extration.document_model.parsers.xml_parser'
        else:
            raise ValueError('Parser for file type "{}" does not exist'.format(file_type))

        module = importlib.import_module(module)
        class_ = getattr(module, class_name)
        return class_()


class Parser:
    @classmethod
    def read_file(cls, filename: str) -> Document:
        with open(filename, 'r', encoding='utf-8') as fp:
            content = fp.read()
        return cls.read(content)

    @classmethod
    def read(cls, content: str) -> Document:
        raise NotImplemented

    @staticmethod
    def write(doc: Document, encoding='utf8', xml_declaration=True, pretty_print=False) -> bytes:
        """ convert a Document to xml in a byte array
        :param doc: Document instance
        :param encoding: use encodings supported by lxml (utf8, ascii, ect.)
        :param xml_declaration: boolean, include xml declaration (recommended)
        :param pretty_print: boolean, print elements indented across different lines (for debugging)
        """
        tree = Parser.to_element_tree(doc)
        return etree.tostring(tree, encoding=encoding, xml_declaration=xml_declaration, pretty_print=pretty_print)

    @staticmethod
    def to_element_tree(doc: Document) -> etree.ElementTree:
        """ convert a document into an lxml ElementTree

        :param doc: Document instance
        :returns lxml.etree ElementTree instance
        """
        elements = []
        tags = []
        root, sub, tag = None, None, None
        # Document must have a root element
        if not doc.tags[0].end - doc.tags[0].start == len(doc.text):
            raise ValueError('{} is not a valid root element'.format(doc.tags[0]))

        for i, tag in enumerate(doc.tags):
            next_tag = doc.tags[i + 1] if i < len(doc.tags) - 1 else None
            # This is the root element
            if not len(elements):
                root = etree.Element(tag.name, attrib=tag.attrib)
                root.text = doc.text[tag.start:next_tag.start]
                elements.append(root)
                tags.append(tag)
            # If tag is a child of the last element
            elif tags[-1].overlaps(tag):
                # A tag may only have one parent
                intersection = tags[-1].intersection(tag)
                if not len(intersection) == len(tag):
                    raise ValueError(
                        '{} cannot be a child of {} with intersection {}'.format(tag, tags[-1], len(intersection)))
                sub = etree.SubElement(elements[-1], tag.name, tag.attrib)
                # if the tag has children
                if next_tag is not None and tag.overlaps(next_tag):
                    sub.text = doc.text[tag.start:next_tag.start]
                else:
                    sub.text = doc.text[tag.start:tag.end]
                elements.append(sub)
                tags.append(tag)
            else:
                sibling_tag, sibling_element = None, None
                # Step out until we find the parent node
                finished = tags[-1].overlaps(tag)
                while not finished and len(tags) > 1:
                    sibling_element = elements.pop()
                    sibling_tag = tags.pop()
                    sibling_element.tail = doc.text[sibling_tag.end:tags[-1].end]
                    if tags[-1].overlaps(tag):
                        finished = True

                # Put the tail on the previous sibling
                if sibling_element is not None:
                    sibling_element.tail = doc.text[sibling_tag.end:tag.start]

                intersection = tags[-1].intersection(tag)
                if not len(intersection) == len(tag):
                    raise ValueError(
                        '{} cannot be a child of {} with intersection {}'.format(tag, tags[-1], len(intersection)))
                sub = etree.SubElement(elements[-1], tag.name, tag.attrib)
                # If the next tag is a child of this tag
                if next_tag is not None and tag.overlaps(next_tag):
                    sub.text = doc.text[tag.start:next_tag.start]
                else:
                    sub.text = doc.text[tag.start:tag.end]
                elements.append(sub)
                tags.append(tag)

        if sub is not None and tag is not None:
            sub.tail = doc.text[tag.end:len(doc.text)]

        # Remove any newline elements added in the read step
        for element in root.iter():
            if element.text is not None:
                element.text = element.text.replace('\n', '')
            if element.tail is not None:
                element.tail = element.tail.replace('\n', '')
        return etree.ElementTree(root)

    @staticmethod
    def _extract_xml_indices(model: Document, content: str):
        offset = re.match('<\?xml version=(?:"|\')1.0(?:"|\') encoding=(?:"|\')(?:UTF-8|UTF8)(?:"|\')\?>', content, flags=re.IGNORECASE).span()[1]
        tag_pattern = re.compile('([ \n]){0,1}<.*?>(\n){0,1}')
        for idx, token in enumerate(model.tokens):
            # Skip spaces or xml tags just before the start of a token.
            # That means move the offset from the end of the last to the beginning of the next
            while True:
                if content[offset].isspace():  # Find the space that can't match to ' '
                    offset += 1
                    continue
                next_tag = tag_pattern.match(content[offset:])
                if next_tag:
                    offset += next_tag.end()
                else:
                    break
            # Skip tokens that are line breaks as they are artificial and do not exist in the xml
            if token.text == '\n':
                continue

            # Start with offset and end pointing to where the token starts in the xml.
            # After the loop the end will point where the last character of the token ends in the xml.
            end = offset
            for char in escape_characters_for_xml(token.text).strip():
                if content[end] == '<':
                    # Tags may be found inside a token, usually because of issues with text extraction from pdf
                    # Move after the tags before trying to match the next character
                    next_tag = tag_pattern.match(content[end:])
                    while next_tag:
                        end += next_tag.end()
                        next_tag = tag_pattern.match(content[end:])
                if char == content[end]:
                    end += 1
                else:
                    logger.warning('Something went wrong with token {}'.format(token.text))
            token.source = Interval(offset, end)
            offset = end
