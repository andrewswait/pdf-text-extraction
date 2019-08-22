import unittest
from extration.pdf_to_xml.document import TextBox, Text, make_text_content


class TestDataLoader(unittest.TestCase):
    def test_make_text_content_no_formatting(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, text_raw, 'Wrong formatting')

    def test_make_text_content_bold_start(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['b', 'b', 'b', 'b', 'b', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, '<b>Lorem</b> Ipsum is simply', 'Wrong formatting')

    def test_make_text_content_bold_end(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'b', 'b', 'b', 'b', 'b', 'b']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, 'Lorem Ipsum is <b>simply</b>', 'Wrong formatting')

    def test_make_text_content_bold_middle(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'b', 'b', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, 'Lorem Ipsum <b>is</b> simply', 'Wrong formatting')

    def test_make_text_content_bold_and_italic(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['b', 'b', 'b', 'b', 'b', 'n', 'i', 'i', 'i', 'i', 'i', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, '<b>Lorem</b> <i>Ipsum</i> is simply', 'Wrong formatting')

    def test_make_text_content_bold_and_italic_ovelapping(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['n', 'n', 'n', 'n', 'n', 'n', 'bi', 'bi', 'bi', 'bi', 'bi', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, 'Lorem <b><i>Ipsum</i></b> is simply', 'Wrong formatting')

    def test_make_text_content_bold_and_italic_overlapping_extend_left(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['b', 'b', 'b', 'b', 'b', 'b', 'bi', 'bi', 'bi', 'bi', 'bi', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, '<b>Lorem <i>Ipsum</i></b> is simply', 'Wrong formatting')

    def test_make_text_content_bold_and_italic_overlapping_extend_right(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['n', 'n', 'n', 'n', 'n', 'n', 'bi', 'bi', 'bi', 'bi', 'bi', 'i', 'i', 'i', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, 'Lorem <b><i>Ipsum</i></b><i> is</i> simply', 'Wrong formatting')

    def test_make_text_content_bold_and_italic_overlapping_extend(self):
        text_raw = 'Lorem Ipsum is simply'
        emphasis = ['b', 'b', 'b', 'b', 'b', 'b', 'bi', 'bi', 'bi', 'bi', 'bi', 'i', 'i', 'i', 'n', 'n', 'n', 'n', 'n',
                    'n', 'n']
        text_box = TextBox(0, 0, 0, 0, Text(text_raw, '', 0, emphasis))
        text = make_text_content(text_box)
        self.assertEqual(text, '<b>Lorem <i>Ipsum</i></b><i> is</i> simply', 'Wrong formatting')


if __name__ == '__main__':
    unittest.main()
