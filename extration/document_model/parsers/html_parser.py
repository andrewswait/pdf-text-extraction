from .base import Parser
from extration.document_model import Document
from bs4 import BeautifulSoup


class HtmlParser(Parser):
    @classmethod
    def read(cls, content: str):
        parsed_html = cls._parse_html(content)
        return Document(parsed_html)

    @classmethod
    def _parse_html(cls, content: str):
        table_position_in_content = []
        parsed_tables = []
        extracted_tables = []

        content = HtmlParser._replace_tags_and_special_chars(content)

        content = BeautifulSoup(content, features="lxml")
        tables = content.find_all('table')

        # By default a <p> tag doesn't add a newline between next element
        # Skip adding newline if a <p> tag is inside a <td> tag
        for p in content.find_all('p'):
            if p.parent.name == 'td':
                continue
            else:
                p.replace_with('\n' + p.text)

        # Get the index of each table in the content (their position in the content)
        # Extract tables and append them to a list
        for table in tables:
            table_position_in_content.append(content.get_text().index(table.get_text()))
            extracted_tables.append(table.extract())

        # Put each parsed table back in content at it's corresponding index
        for idx, table in enumerate(extracted_tables):
            parsed_tables.append(HtmlParser._parse_table_element(table))
            sum_parsed_table_len = 0 if idx == 0 else sum_parsed_table_len + len(''.join(parsed_tables[idx - 1]))
            content = content.get_text()[:(table_position_in_content[idx] + sum_parsed_table_len - 1)] + ''.join(
                parsed_tables[idx]) + content.get_text()[(table_position_in_content[idx] + sum_parsed_table_len - 1):]
            content = BeautifulSoup(content, features="lxml")

        return content.get_text()

    @classmethod
    def _replace_tags_and_special_chars(cls, content):
        content = content.replace('\n', ' ') \
            .replace('<br>', '\n') \
            .replace('<div>', '\n') \
            .replace('</div>', '\n') \
            .replace('\x91', '’') \
            .replace('\x92', '’') \
            .replace('\x93', '“') \
            .replace('\x94', '“') \
            .replace('\x95', '•') \
            .replace('\x96', '-') \
            .replace('\u200b', '') \
            .replace('\x97', '—') \
            .replace('\x98', '˜') \
            .replace('\x99', '™')
        return content

    @classmethod
    def _parse_table_element(cls, table_element):
        parsed_table = []
        for tr in table_element.find_all('tr'):
            td = tr.find_all('td')
            td = [ele.get_text(strip=True) if ele.find('div') or ele.find('p') is not None else ele.get_text() for ele in td]
            parsed_table.append('\n' + ' '.join(td) + '\n')
        parsed_table = [str(i) for i in parsed_table]
        return parsed_table
