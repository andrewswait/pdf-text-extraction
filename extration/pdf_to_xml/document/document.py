from enum import Enum
from collections import OrderedDict, Counter


class BlockType(Enum):
    Text = 0
    Footer = 1
    Header = 2
    Table = 3


class Text:
    def __init__(self, text: str, font: str, size: int, emphasis: list=None):
        self.text = text
        self.font = font
        self.size = size
        self.emphasis = emphasis

    def __repr__(self):
        return self.text


class BoundingBox:
    def __init__(self, top: int, left: int, width: int, height: int):
        self.top = top
        self.left = left
        self.height = height
        self.width = width
        self.right = left + width
        self.bottom = top + height

    def __repr__(self):
        return '{}(top: {}, left: {}, height: {}, width: {})'.format(type(self).__name__, self.top, self.left, self.height, self.width)

    def is_contained(self, bbox, tolerance=0):
        """I contained in bbox provided as argument"""
        if bbox.top <= self.top + tolerance and bbox.left <= self.left + tolerance:
            if bbox.bottom >= self.bottom - tolerance and bbox.right >= self.right - tolerance:
                return True
        return False

    def overlaps(self, bbox):
        if bbox is None or self.top > bbox.bottom or bbox.top > self.bottom:
            return False
        if self.left > bbox.right or bbox.right < self.left:
            return False
        return True

    def expand_to_contain(self, bbox):
        self.top = min(self.top, bbox.top)
        self.left = min(self.left, bbox.left)
        self.right = max(self.right, bbox.right)
        self.bottom = max(self.bottom, bbox.bottom)
        self.height = self.bottom - self.top
        self.width = self.right - self.left


class TextBox(BoundingBox):
    def __init__(self, top: int, left: int, width: int, height: int, content: Text):
        BoundingBox.__init__(self, top, left, width, height)
        self.content = content

    @property
    def text(self):
        return self.content.text

    def __repr__(self):
        return super(TextBox, self).__repr__() + ': {}'.format(self.text)


class ImageBox(BoundingBox):
    def __init__(self, top: int, left: int, width: int, height: int, file_name: str, file_stream):
        BoundingBox.__init__(self, top, left, width, height)
        self.file_id = None
        self.file_name = file_name
        self.file_stream = file_stream


class Block(BoundingBox):
    def __init__(self, top: int, left: int, width: int, height: int, block_type=BlockType.Text):
        BoundingBox.__init__(self, top, left, width, height)
        self.type = block_type


class Page:
    def __init__(self, number: int, width: int, height: int):
        self.number = number
        self.width = width
        self.height = height
        self._boxes = []
        self._lines = OrderedDict()

    def __getitem__(self, item):
        return self._boxes[item]

    def __iter__(self):
        return iter(self._boxes)

    def __len__(self):
        return len(self._boxes)

    def __repr__(self):
        return 'Page (no: {}, width: {}, height: {})'.format(self.number, self.width, self.height)

    def get_lines(self):
        return self._lines

    def get_font_sizes(self):
        sizes = Counter()
        for text in [b for b in self._boxes if isinstance(b, TextBox)]:
            sizes[text.content.size] += 1
        return sizes

    def correct_width(self):
        self.width = max(max((box.right for box in self._boxes if isinstance(box, TextBox)), default=self.width),
                         self.width)

    def correct_height(self):
        self.height = max(max((box.bottom for box in self._boxes if isinstance(box, TextBox)), default=self.width),
                          self.height)

    def add_box(self, box):
        self._boxes.append(box)
        if isinstance(box, TextBox):
            if box.top not in self._lines:
                self._lines[box.top] = []
            self._lines[box.top].append(len(self._boxes) - 1)

    def get_contained_text_boxes(self, block: Block):
        return [box for box in self._boxes if
                isinstance(box, TextBox) and
                box.is_contained(block)]

    def get_containing_block(self, box: TextBox):
        return next((block for block in self._boxes if
                     isinstance(block, Block) and
                     box.is_contained(block)), None)

    def delete_boxes(self, boxes):
        if not isinstance(boxes, list) and not isinstance(boxes, set):
            self._boxes.remove(boxes)
        else:
            for box in boxes:
                self._boxes.remove(box)

    def keep_outer_blocks(self):
        """
        :param rectangles: list of bounding boxes (top, left, bottom, right)
        :return: outer bounding boxes (only the largest bbox when bboxes intersect)
        """
        to_remove = []
        blocks = [b for b in self._boxes if isinstance(b, Block)]
        for i, bbox1 in enumerate(blocks):
            for j, bbox2 in enumerate(blocks[i + 1:]):
                if bbox1.is_contained(bbox2):
                    to_remove.append(bbox1)
                    break
                elif bbox2.is_contained(bbox1):
                    to_remove.append(bbox2)
        self.delete_boxes(set(to_remove))


class Document:
    def __init__(self):
        self._pages = []

    def __getitem__(self, i: int):
        return self._pages[i]

    def __iter__(self):
        return iter(self._pages)

    def __len__(self):
        return len(self._pages)

    def add_page(self, page):
        self._pages.append(page)
