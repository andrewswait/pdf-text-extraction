from html.parser import HTMLParser
import xml


class HtmlStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        if d != '\n':
            self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)
