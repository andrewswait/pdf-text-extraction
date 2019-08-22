import unittest
import os
from extration.tests import TEST_DATA_DIR
from extration.document_model.document_model import Interval, Section, SectionTypes
from extration.document_model.parsers import ParserFactory


class TestFindParagraphs(unittest.TestCase):
    def setUp(self):
        self._folder = os.path.join(TEST_DATA_DIR, 'tokenize')

    def get_document(self, filename):
        with open(os.path.join(self._folder, filename), 'r', encoding='utf-8') as fd:
            content = fd.read()
        parser = ParserFactory.get_parser(content, filename[-3:])
        return parser.read(content)

    def get_correct_paragraphs(self, filename):
        with open(os.path.join(self._folder, filename), 'r', encoding='utf-8') as fd:
            return [paragraph.replace('\n', ' ') for paragraph in fd.read().split('☃')]

    def test_section_find_paragraph_1(self):
        doc = self.get_document('tokenize_test_1.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.paragraphs), 9, 'Wrong number of paragraphs')

    def test_section_find_paragraph_2(self):
        doc = self.get_document('tokenize_test_2.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.paragraphs), 1, 'Wrong number of paragraphs')

    def test_section_find_paragraph_3(self):
        doc = self.get_document('tokenize_test_3.txt')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEquals(len(section.paragraphs), 1, 'Wrong number of paragraphs')

    def test_paragraph_splitter_1(self):
        doc = self.get_document('paragraph_splitter_1.xml')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEqual(len(section.paragraphs), 3, 'Not all paragraphs split')
        self.assertEqual(len(section.sentences), 6, 'Not all sentences included')

        correct_paragraphs = self.get_correct_paragraphs('paragraph_splitter_1_paragraphs.txt')
        self.assertEqual(len(section.paragraphs), len(correct_paragraphs), 'Not all paragraphs split')
        for paragraph, correct_paragraph in zip(section.paragraphs, correct_paragraphs):
            self.assertEqual(' '.join(paragraph.text.split()), ' '.join(correct_paragraph.split()),
                             'Sentences not split correctly')

    def test_paragraph_splitter_2(self):
        doc = self.get_document('paragraph_splitter_2.xml')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEqual(len(section.paragraphs), 5, 'Not all paragraphs split')
        self.assertEqual(len(section.sentences), 11, 'Not all sentences included')

        correct_paragraphs = self.get_correct_paragraphs('paragraph_splitter_2_paragraphs.txt')
        self.assertEqual(len(section.paragraphs), len(correct_paragraphs), 'Not all paragraphs split')
        for paragraph, correct_paragraph in zip(section.paragraphs, correct_paragraphs):
            self.assertEqual(' '.join(paragraph.text.split()), ' '.join(correct_paragraph.split()),
                             'Sentences not split correctly')

    def test_paragraph_splitter_3(self):
        doc = self.get_document('paragraph_splitter_3.xml')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEqual(len(section.paragraphs), 3, 'Not all paragraphs split')
        self.assertEqual(len(section.sentences), 9, 'Not all sentences included')

        correct_paragraphs = self.get_correct_paragraphs('paragraph_splitter_3_paragraphs.txt')
        self.assertEqual(len(section.paragraphs), len(correct_paragraphs), 'Not all paragraphs split')
        for paragraph, correct_paragraph in zip(section.paragraphs, correct_paragraphs):
            self.assertEqual(' '.join(paragraph.text.split()), ' '.join(correct_paragraph.split()),
                             'Sentences not split correctly')

    def test_paragraph_splitter_4(self):
        doc = self.get_document('paragraph_splitter_4.xml')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEqual(len(section.paragraphs), 3, 'Not all paragraphs split')
        self.assertEqual(len(section.sentences), 5, 'Not all sentences included')

        correct_paragraphs = self.get_correct_paragraphs('paragraph_splitter_4_paragraphs.txt')
        self.assertEqual(len(section.paragraphs), len(correct_paragraphs), 'Not all paragraphs split')
        for paragraph, correct_paragraph in zip(section.paragraphs, correct_paragraphs):
            self.assertEqual(' '.join(paragraph.text.split()), ' '.join(correct_paragraph.split()),
                             'Sentences not split correctly')

    def test_paragraph_splitter_5(self):
        doc = self.get_document('paragraph_splitter_5.xml')
        section = Section(doc, SectionTypes.Clause, content_idx=Interval(0, len(doc) - 1))
        self.assertEqual(len(section.paragraphs), 11, 'Not all paragraphs split')
        self.assertEqual(len(section.sentences), 21, 'Not all sentences included')

        correct_paragraphs = self.get_correct_paragraphs('paragraph_splitter_5_paragraphs.txt')
        self.assertEqual(len(section.paragraphs), len(correct_paragraphs), 'Not all paragraphs split')
        for paragraph, correct_paragraph in zip(section.paragraphs, correct_paragraphs):
            self.assertEqual(' '.join(paragraph.text.split()), ' '.join(correct_paragraph.split()),
                             'Sentences not split correctly')


if __name__ == '__main__':
    unittest.main()
