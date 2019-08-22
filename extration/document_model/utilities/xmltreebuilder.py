import zipfile
import xml.parsers.expat


class Element(list):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs


class TreeBuilder:
    def __init__(self):
        self.root = Element("root", None)
        self.path = [self.root]

    def start_element(self, name, attrs):
        element = Element(name, attrs)
        self.path[-1].append(element)
        self.path.append(element)

    def end_element(self, name):
        assert name == self.path[-1].name
        self.path.pop()

    def char_data(self, data):
        self.path[-1].append(data)

    def parse_xml(self, filename):
        parser = xml.parsers.expat.ParserCreate()
        # assign the handler functions
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.CharacterDataHandler = self.char_data

        # get content xml data from OpenDocument file
        ziparchive = zipfile.ZipFile(filename, 'r')
        xmldata = ziparchive.read('word/document.xml')
        ziparchive.close()

        # parse the data
        parser.Parse(xmldata, True)

    def showtree(self, node=None, prefix=''):
        if not node:
            node = self.root
        print('{0}, {1}'.format(prefix, node.name))
        for e in node:
            if isinstance(e, Element):
                self.showtree(e, prefix + "  ")
            else:
                print('{0} {1}'.format(prefix, e))