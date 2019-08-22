from .base import Parser
from extration.document_model import Document


class TextParser(Parser):
    @classmethod
    def read_file(cls, filename: str) -> Document:
        with open(filename, 'r', encoding='utf-8') as fp:
            content = fp.read()
        return cls.read(content)

    @classmethod
    def read(cls, content: str) -> Document:
        return Document(content)
