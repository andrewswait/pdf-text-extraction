from typing import List
import copy
import re
import os
import numpy as np
import logging
from unidecode import unidecode
from extration.document_model.nlp.tokenizer import tokenize_text
from .interval import Interval

LOGGER = logging.getLogger(__name__)


def setattrib(obj, name: str, value):
    setattr(obj, name, value)
    return obj


def shift(interval: Interval, n: int, lim: int) -> Interval:
    ret = copy.deepcopy(interval)
    ret.start = max(min(ret.start + n, lim), 0)
    ret.end = max(min(ret.end + n, lim), 0)
    return ret


class Token(Interval):
    """ A Interval representing word like units of text with a dictionary of features """

    def __init__(self, document, start: int, end: int, pos: str, shape: str, text: str):
        """
        Represent a Token with all its features, i.e. word, pos tag and shape.
        :param document: the document object containing the token
        :param start: start of token in document text
        :param end: end of token in document text
        :param norm: normalized form of token text
        :param pos: part of speach of the token
        :param shape: integer label describing the shape of the token (particular to cog+)
        :param text: this is the text representation of token
        """
        Interval.__init__(self, start, end)
        self._doc = document
        self.features = {'pos': pos, 'shape': shape}
        self.token_text = text
        self.source = None
        self.index = None

    @property
    def text(self):
        return self._doc.text[self.start:self.end]
    
    @property
    def norm(self):
        if self.token_text == '\n':
            return 'NL'
        return re.sub('\d', 'D', self.token_text.lower().strip(' '))

    def __getitem__(self, item):
        return self.features[item]

    def __repr__(self):
        if not self.source:
            return 'Token({}, {}, {}, {})'.format(self.text, self.start, self.end, self.features)
        else:
            return 'Token({}, {}({}), {}({}), {})'.format(self.text, self.start, self.source.start, self.end,
                                                          self.source.end, self.features)


class Sentence(Interval):
    """ Interval corresponding to a Sentence"""

    def __init__(self, document, start: int, end: int):
        Interval.__init__(self, start, end)
        self._doc = document
        self.index = None

    @property
    def text(self):
        return self._doc.text[self._doc.tokens[self.start].start:self._doc.tokens[self.end].end]

    def __repr__(self):
        return 'Sentence({}, {}, {})'.format(self.start, self.end, self.text)


class Paragraph(Interval):
    """ Interval corresponding to a Paragraph"""
    def __init__(self, document, start: int, end: int, number: str):
        Interval.__init__(self, start, end)
        self._doc = document
        self.number = number

    @property
    def text(self):
        return self._doc.text[self._doc.tokens[self.start].start:self._doc.tokens[self.end].end]

    def __repr__(self):
        return 'Paragraph({}, {}, {})'.format(self.start, self.end, self.text)


class Tag(Interval):
    """ An interval representing an xml tag  """

    def __init__(self, start: int, end: int, name: str, attrib: dict):
        """
        :param start: start of tag text in document
        :param end: end of tag text in document
        :param name: tag name (e.g. emphasis)
        :param attrib: tag attributes (e.g. {emphasis: 'strong'})
        """
        Interval.__init__(self, start, end)
        self.name = name
        self.attrib = attrib

    def __getitem__(self, item):
        return self.attrib[item]

    def __repr__(self):
        return 'Tag({}, {}, {}, {})'.format(self.start, self.end, self.name, self.attrib)


class Document:
    """
    A document is a combination of text and the positions of the tags and elements in that text.
    """

    def __init__(self,  text: str = None, tags: List[Tag] = None, xml=None):
        """
        :param text: document text as a string
        :param tags: list of Tag objects
        :param xml: document content as xml
        """
        if text is None or text == '':
            self.text, self.tokens = '', []
            return
        self.text = text
        tokens, pos_tags, shapes = zip(*tokenize_text(text))
        self.tokens = self._build_tokens(tokens, pos_tags, shapes, text)
        self.feature_vector, self.pages, self.quality = None, [], 0
        if tags:
            self.tags = list(map(lambda item, idx: setattrib(item, 'index', idx), tags, range(len(tags))))
        if xml:
            self.pages = self._find_pages()
            self.xml = xml
        else:
            self.pages = []
            self.xml = None

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            return self.tokens[key].text

    def __repr__(self):
        if self.tags:
            return 'Document(tokens={}, tags={}, text={})'.format(self.tokens, self.tags, self.text)
        else:
            return 'Document(tokens={}, tags={})'.format(self.tokens, self.text)

    @property
    def feature_size(self):
        return self.feature_vector.shape[1] if self.feature_vector is not None else 0

    def _build_tokens(self, word_tokens, pos_tags, shapes, text):
        """
        Merge the word, pos tag and shape of each word to a Token class. The Token contains the above information
        plus the position of each word in the original text.
        :param word_tokens: List of words (strings)
        :param pos_tags: List of pos tags (strings)
        :param shapes: List of shape representations (strings)
        :param text: Document text
        :return: List of "Token" instances one for each input token
        """
        """ Calculate the span of each token,
         find which element it belongs to and create a new Token instance """
        tokens, missing = [], []
        offset, index = 0, -1
        for token, pos_tag, shape in zip(word_tokens, pos_tags, shapes):
            index += 1
            while offset < len(text) and (text[offset] == '\n' or text[offset].isspace()):
                if text[offset] == '\n':
                    tokens.append(Token(self, offset, offset + 1, 'NL', 'NL', '\n'))
                offset += 1

            # Correct issue with tokenization of ".
            # This is the case where in the text " is followed by double ' (can happen with OCR).
            # Both tokens are turned into \'\', so the first will match the double ' instead of the  "
            # Solution: if the token is \'\' try first to force match with " in text and make sure it does not get
            # mixed up with a \'\' afterwards
            pos = -1
            if token in ['\'\'', '``']:
                pos_double = text.find('\'\'', offset)
                pos_quote = text.find('"', offset, offset + len(token) + 1)
                if 0 <= pos_quote < pos_double or (pos_double < 0 and pos_quote >= 0 ):
                    token = '"'
                    pos = pos_quote

            if pos < 1:
                pos = text.find(token, offset, offset + max(50, len(token)))
            if pos >= 0 and (pos - offset <= max(len(token), 3) or len(missing) > 0):
                if missing:
                    start = tokens[-1].end if len(tokens) > 1 else 0
                    for m in missing:
                        while text[start].isspace() or '\n' in text[start]:
                            if '\n' in text[start]:
                                tokens.append(Token(self, start, start + 1, 'NL', 'NL', '\n'))
                            start += 1
                        length = len(m[0])
                        # If the token '\'\'' or '``' came from a " the length should be 1
                        if m[0] in ['\'\'', '``'] and text.find('"', start, start + 1) == 0:
                            length = 1
                        tokens.append(Token(self, start, start + length, m[0], m[1], m[2]))
                        start = start + length
                    missing = []
                tokens.append(Token(self, pos, pos + len(token), pos_tag, shape, token))
                offset = pos + len(token)
            else:
                missing.append((pos_tag, shape, token))
                if pos_tag not in ['\'\'', '``']:
                    LOGGER.debug('Token "{}" not found'.format(token))
        return list(map(lambda item, idx: setattrib(item, 'index', idx), tokens, range(len(tokens))))

    def _find_pages(self):
        """
        Identify which tokens belong to which page.
        :return: List of Intervals each one pointing to the tokens belonging to a page.
        """
        if self.tags is None:
            return
        page_tags = dict([(int(t.attrib['number']), t) for t in self.tags if t.name == 'page'])
        pages_intervals = dict([(key, None) for key in page_tags.keys()])
        if len(pages_intervals) == 0:
            return []
        max_page = max([key for key in pages_intervals.keys()])
        page = 0
        for token in self.tokens:
            while page not in page_tags or not token.overlaps(page_tags[page]):
                if page > max_page:
                    page = max_page
                    break
                page += 1

            if pages_intervals[page] is None:  # Token is the begining of a page
                pages_intervals[page] = Interval(token.index, token.index)
            else:  # Token is inside the page. The last is going to be the end
                pages_intervals[page].end = token.index
        return [value for value in pages_intervals.values() if value is not None]

    def get_containing_page(self, interval: Interval):
        """
        Get the page containing given tokens. Tokens are defined as an interval on the document token list.
        Returns the starting page.
        :param interval: specifying the token range
        :return: the page number
        """
        page = next((i for i, p in enumerate(self.pages) if p.overlaps(Interval(interval.start, interval.start))), None)
        return page + 1 if page is not None else None

    def extract_document_part(self, token_range: Interval):
        """
        Create a document object from a part of the current document
        :param token_range: range of tokens to include in the new document
        :return: Document object
        """
        if self.tokens[token_range.end].text == '\n':
            token_range.end -= 1

        text_interval = Interval(self.tokens[token_range.start].start,
                                 self.tokens[token_range.end].end)
        from copy import deepcopy
        tags = deepcopy([e for e in self.tags if e.overlaps(text_interval)])
        tags = sorted(sorted(tags, key=lambda x: x.end, reverse=True), key=lambda x: x.start)

        # Calculate the total range using only text and emphasis tags as they are the only ones that should have text.
        # Otherwise we may get text from other boxes of the same block even thought they are not in the range
        tags_box_only = [item for item in tags if item.name in ['box', 'text', 'emphasis']]
        text_range = Interval(min(tags_box_only, key=lambda x: x.start).start,
                              max(tags_box_only, key=lambda x: x.end).end)
        text = self.text[text_range.start:text_range.end]
        tags[0].start = text_range.start
        tags[0].end = text_range.end
        for tag in tags:
            if text_range.start > tag.start:
                tag.start = 0
            else:
                tag.start -= text_range.start
            if tag.end > text_range.end:
                tag.end = text_range.end - text_range.start
            else:
                tag.end -= text_range.start

        return Document(text, tags)

    def get_page_tokens(self, page_no):
        if 0 <= page_no < len(self.pages):
            return self.tokens[self.pages[page_no].start:self.pages[page_no].end + 1]
        else:
            return []

    def get_page_words(self, page_no):
        if 0 <= page_no < len(self.pages):
            return self[self.pages[page_no].start:self.pages[page_no].end + 1]
        else:
            return ''

    def get_page_text(self, page_no):
        if 0 <= page_no < len(self.pages):
            return self.get_section_text(self.pages[page_no])
        else:
            return ''

    def get_section_tokens(self, token_range: Interval):
        return self.tokens[token_range.start:token_range.end + 1]

    def get_section_words(self, token_range: Interval):
        return self[token_range.start:token_range.end + 1]

    def get_section_text(self, token_range: Interval):
        return self.text[self.tokens[token_range.start].start:self.tokens[token_range.end].end]

    def get_content_interval(self, token_range: Interval):
        """
        Get the indices on the document xml (if exists) that correspond to a range of tokens. Effectively, find the
        indices on the xml that contains all the tokens of a range.
        :param token_range: range on list of tokens
        :return: interval on the xml
        """
        while self.tokens[token_range.start].text == '\n':
            token_range.start += 1
        while self.tokens[token_range.end].text == '\n':
            token_range.end -= 1
        if token_range.start > token_range.end:
            return None
        if self.tokens[token_range.start].source is None or self.tokens[token_range.end].source is None:
            return None
        return Interval(self.tokens[token_range.start].source.start,
                        self.tokens[token_range.end].source.end)
