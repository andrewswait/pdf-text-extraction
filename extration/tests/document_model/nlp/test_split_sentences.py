import unittest
import os
from extration.tests import TEST_DATA_DIR
from extration.document_model.nlp import split_sentences
from extration.document_model import Interval, Section, SectionTypes
from extration.document_model.parsers import ParserFactory


class TestSplitSentences(unittest.TestCase):
    def setUp(self):
        self._folder = os.path.join(TEST_DATA_DIR, 'tokenize')

    def get_document(self, filename):
        with open(os.path.join(self._folder, filename), 'r', encoding='utf-8') as fd:
            content = fd.read()
        parser = ParserFactory.get_parser(content, filename[-3:])
        return parser.read(content)

    def test_sentence_splitter_text_1(self):
        doc = self.get_document('tokenize_test_1.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.sentences), 12, 'Not all sentences extracted')
        self.assertEquals(doc.tokens[section.sentences[0].start].text, '21.1', 'Sentence start not correct')
        self.assertEquals(doc.tokens[section.sentences[0].end].text, '.', 'Sentence end not correct')

    def test_sentence_splitter_text_2(self):
        doc = self.get_document('tokenize_test_2.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.sentences), 1, 'Not all sentences extracted')

    def test_sentence_splitter_text_3(self):
        doc = self.get_document('tokenize_test_3.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.sentences), 3, 'Not all sentences extracted')

    def test_sentence_splitter_1(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_1.xml').text)
        self.assertEqual(len(sentences), 3, 'Not all sentences split')

    def test_sentence_splitter_2(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_2.xml').text)
        self.assertEqual(len(sentences), 9, 'Not all sentences split')

    def test_sentence_splitter_3(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_3.xml').text)
        self.assertEqual(len(sentences), 5, 'Not all sentences split')

    def test_sentence_splitter_4(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_4.xml').text)
        self.assertEqual(len(sentences), 4, 'Not all sentences split')

    def test_sentence_splitter_5(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_5.xml').text)
        self.assertEqual(len(sentences), 11, 'Not all sentences split')

    def test_sentence_splitter_6(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_6.xml').text)
        self.assertEqual(len(sentences), 7, 'Not all sentences split')

    def test_sentence_splitter_7(self):
        sentences = split_sentences(self.get_document('sentence_splitter_text_7.xml').text)
        self.assertEqual(len(sentences), 15, 'Not all sentences split')

    def test_sentence_splitter_8(self):
        with open(os.path.join(self._folder, 'sentence_splitter_text_8.txt'), 'r', encoding='utf-8') as f:
            content = f.read()
        sentences = split_sentences(content)
        self.assertEqual(len(sentences), 2, 'Not all sentences split')


if __name__ == '__main__':
    unittest.main()
