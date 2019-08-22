import logging
import unittest
import os
from annual_reports.tests import TEST_DATA_DIR, TEST_BASE_DIR
from annual_reports.document_model.data import DATA_DIR
from annual_reports.document_model.nlp.embeddings import load_embeddings
from annual_reports.document_model.parsers import ParserFactory
from annual_reports.document_model.document_model import Document, Sentence

LOGGER = logging.getLogger(__name__)


class TestModel(unittest.TestCase):
    def setUp(self):
        logging.config.fileConfig(os.path.join(TEST_BASE_DIR, 'logging.ini'), disable_existing_loggers=False)
        self._embeddings = {'word': load_embeddings(os.path.join(DATA_DIR, 'embeddings', 'WORD_WORD2VEC_20_200.bin')),
                            'pos': load_embeddings(os.path.join(DATA_DIR, 'embeddings', 'POS_WORD2VEC_20_25.bin')),
                            'shape': load_embeddings(os.path.join(DATA_DIR, 'embeddings', 'SHAPE_WORD2VEC_20_25.bin'))}

        self._data_folder = os.path.join(TEST_DATA_DIR, 'contracts')

    def _parse_file(self, filename):
        with open(os.path.join(self._data_folder, filename), 'r', encoding='utf-8') as f:
            content = f.read()
        return ParserFactory.get_parser(content).read(content)

    def _get_document(self, filename: str):
        document = self._parse_file(filename)
        document.create_features(self._embeddings)
        return document

    def test_create(self):
        document = self._get_document('employment_agreement_1.xml')
        self.assertIsInstance(document, Document, 'Document not created properly')
        self.assertEquals(len(document), 10557, 'Token number is not correct')
        self.assertEquals(len(document.pages), 15, 'Page number is not correct')
        self.assertEqual(document.feature_vector.size, 2639250, 'Feature size is not correct')
        # Get features by sentence
        features = document.get_features_by_sentence([Sentence(document, 19, 92)])
        self.assertEquals(features.shape[0], 1, 'Sentences not found correctly')
        # Get features by sentence with padding
        features = document.get_features_by_sentence([Sentence(document, 19, 92)], 50)
        self.assertEquals(features.shape[1], 50, 'Sentences not found correctly')


if __name__ == '__main__':
    unittest.main()
