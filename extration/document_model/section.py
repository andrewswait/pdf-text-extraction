import logging
import re
from enum import Enum
from extration.document_model.nlp import split_sentences, find_paragraphs
from extration.document_model import Interval, Document, Sentence, Paragraph

LOGGER = logging.getLogger(__name__)


class SectionTypes(Enum):
    EntireDocument = 0
    CoverPage = 1
    TableOfContents = 2
    Introduction = 3
    Recitals = 4
    Section = 5
    Clause = 6
    Paragraph = 7
    Signatures = 8
    Appendix = 9
    Exhibit = 10
    Schedule = 11
    Annex = 12
    Attachment = 13
    LeaseDetails = 14


class Section(object):
    def __init__(self, document: Document, type: SectionTypes, level: int = None, name: str = None,
                 header_idx: Interval = None, numbering_idx: int = None, content_idx: Interval = None):
        self._document = document
        self.type = type
        self.level = level
        self.parent = None
        self.index = None
        self.categories = []
        self.header_idx = header_idx
        self.numbering_idx = numbering_idx

        self.header = ''
        if header_idx is not None:
            self.header = re.sub('(\s)+', ' ', self._document.get_section_text(self.header_idx)).strip()

        self.name = ''
        self.number = ''
        if name is None and self.numbering_idx is not None and self.header_idx is not None:
            self.name = re.sub('(\s)+', ' ', self.header[self.numbering_idx:]).strip(' .-:\n')
            self.number = re.sub('(\s)+', ' ', self.header[:self.numbering_idx]).strip(' -:\n')
        elif name is None and self.header_idx is not None:
            self.name = re.sub('(\s)+', ' ', self.header).strip(' .-:\n')

        self._content_idx = content_idx
        self._set_content()

    @property
    def content_idx(self):
        return self._content_idx

    @content_idx.setter
    def content_idx(self, value):
        self._content_idx = value
        self._set_content()

    def _set_content(self):
        if self._content_idx:
            self.content = re.sub('( )+', ' ', self._document.get_section_text(self.content_idx))
            self.content = re.sub('^([\n ])*|(([\n ])*)$', '', self.content)
            if self.type.value in [0, 3, 4, 6]:
                self.sentences = self._find_sentences()
                if self.sentences:
                    self.paragraphs = self._find_paragraphs()
            else:
                self.sentences = [Sentence(self._document, self._content_idx.start, self._content_idx.end)]
                self.paragraphs = [Paragraph(self._document, self._content_idx.start, self._content_idx.end, '1')]
        else:
            self.content, self.sentences, self.paragraphs = '', [], []

    def _find_sentences(self):
        sentences = []
        token_offset = self.content_idx.start
        for i, sentence in enumerate(split_sentences(self.content)):
            start_token, char_offset = None, 0
            for token in self._document.tokens[token_offset:self.content_idx.end + 1]:
                if token.text == '\n':
                    continue
                token_pos = sentence[2].find(token.text, char_offset)
                if token_pos >= 0 and start_token is None:
                    start_token = token.index
                elif token_pos >= 0:
                    token_offset = token.index
                else:
                    break
                char_offset = token_pos + len(token.text)

            if start_token is not None and token_offset >= start_token:
                sentences.append(Sentence(self._document, start_token, token_offset))
                sentences[-1].index = i
            token_offset += 1

        return sentences

    def _find_paragraphs(self):
        sentences = [(item.start, item.end, item.text) for item in self.sentences]
        return [Paragraph(self._document, item[0], item[1], item[2]) for item in find_paragraphs(sentences)]

    def get_paragraph_sentences(self, paragraph):
        return [item for item in self.sentences if item.overlaps(paragraph)]

    def __len__(self):
        return len(self.content_idx)

    def __repr__(self):
        return '{0} -> {1}'.format(self.header, self.content)

    def as_dictionary(self):
        item = {'level': self.level,
                'type': self.categories,
                'index': self.index,
                'parent': self.parent,
                'header': self.header,
                'number': self.number,
                'name': self.name,
                'content': self.content}
        if self._document.xml is not None:
            if self.header_idx is not None:
                index = self._document.get_content_interval(self.header_idx)
                item['headerIdx'] = {'start': index.start, 'end': index.end}
            if self.content_idx:
                index = self._document.get_content_interval(self.content_idx)
                item['contentIdx'] = {'start': index.start, 'end': index.end}
        return item
