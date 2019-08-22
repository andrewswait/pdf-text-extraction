import numpy
import os
import re
from PIL import Image
from math import ceil, floor
from collections import Counter
from ...pdf_to_xml.document import Page, TextBox, Block, BlockType
from ...pdf_to_xml.utilities import gauss, find_contours, image_to_bbox, bbox_to_image, draw_rectangles
from ...pdf_to_xml.utilities import get_outer_bounding_boxes

numbers = re.compile('[0-9]+')
simple_tags = re.compile('<[a-z]>|<\/[a-z]>')
bold_italics = re.compile(' *(<b>|</b>|<i>|</i>) *')


def detect_blocks(page: Page, dimension=10, output_folder=None):
    pg = numpy.zeros((page.height, page.width))
    for box in page:
        if not isinstance(box, TextBox) or not box.text.strip():
            continue
        pg[ceil(box.top):ceil(box.top) + ceil(box.height) + 1,
        floor(box.left):floor(box.left) + ceil(box.width) + 1] = 255
    pg2 = gauss(pg, dimension=dimension).astype(numpy.uint8)
    pg2[numpy.where(pg2 <= 5)] = 0
    pg2[numpy.where(pg2 > 5)] = 255
    im = Image.fromarray(pg2, 'L')
    area_boxes = [item for item in reversed(find_contours(numpy.array(im)))]
    bounding_boxes = get_outer_bounding_boxes(image_to_bbox(area_boxes))
    area_boxes = bbox_to_image(bounding_boxes)

    if output_folder:
        png_name = os.path.join(output_folder, 'page_{}.png'.format(page.number))
        im.save(png_name)
        draw_rectangles(png_name, area_boxes, png_name)

    for item in bounding_boxes:
        page.add_box(Block(
            left=item[0],
            top=item[1],
            width=item[2],
            height=item[3]
        ))


def merge_small_blocks(page: Page, tolerance=20):
    for block in [b for b in page if isinstance(b, Block) and b.width < 50]:
        # Get the first block on the right of the current block and overlaps on the height dimension
        to_right = next((b for b in page if isinstance(b, Block)
                         and b.top - 1 <= block.top and b.bottom + 1 >= block.bottom
                         and b.left >= block.right and b.left - block.right < tolerance), None)
        if to_right:
            to_right.expand_to_contain(block)
    page.keep_outer_blocks()

    for block in [b for b in page if isinstance(b, Block) and b.width < 50]:
        # Get the first block on the left of the current block and overlaps on the height dimension
        to_left = next((b for j, b in enumerate(page) if isinstance(b, Block)
                        and b.top - 1 <= block.top and b.bottom + 1 >= block.bottom
                        and b.right <= block.left and abs(b.right - block.left) < tolerance), None)
        if to_left:
            to_left.expand_to_contain(block)
        page.keep_outer_blocks()


def detect_header_footer(document):
    repetitions = Counter()
    indices = {}
    # Take the top and bottom 15% of page lines and add their text as key to a counter
    # key = 'Text of a line', value = 'times it appears in pages'
    # For each key inserted in the counter, keep the line(s) it appears in each page
    # key = 'Text of line', value = dict{key = page number, value = list of lines}
    for page_no, page in enumerate(document):
        top_margin, bottom_margin = int(page.height * 0.1), int(page.height * 0.9)
        for top, box_indices in [(t, idx) for t, idx in page.get_lines().items() if
                                 t <= top_margin or t >= bottom_margin]:
            text = ' '.join([page[i].text for i in box_indices if isinstance(page[i], TextBox)])
            # Replace numbers with _D_ in order to catch numbering repetitions in footer, e.g Page 3 of 15
            key = numbers.sub('_D_', bold_italics.sub('', text))
            if len(key) == 1:
                continue
            repetitions[key] += 1
            if key not in indices:
                indices[key] = []
            for box_idx in box_indices:
                indices[key].append((page_no, box_idx))

    # Consider header/footer everything that appears in more than 20% of pages
    header_footer = [item[0] for item in repetitions.most_common(10) if
                     item[1] > max(int(len(document) * 0.5), 1)]
    # Get the indices (page, line) of the keys (i.e. lines) to be removed.
    indices = dict([(k, v) for k, v in indices.items() if k in header_footer])

    # Organize lines that have to be removed by page
    indices_per_page = {}
    for idx in indices.values():
        for page, line in idx:
            if page not in indices_per_page:
                indices_per_page[page] = []
            indices_per_page[page].append(line)

    # Group boxes in header and footer
    for page_no, page in enumerate(document):
        if page_no not in indices_per_page:
            continue
        # split between lines that are in header and those in footer, based on middle of page
        # Keep the lowest box for header and the highest for footer
        header_boxes = [page[item] for item in indices_per_page[page_no] if page[item].top < (page.height / 2)]
        footer_boxes = [page[item] for item in indices_per_page[page_no] if page[item].top > (page.height / 2)]

        header, footer = None, None
        if header_boxes:
            header = Block(top=0, left=0,
                           width=page.width, height=max([item.bottom for item in header_boxes]),
                           block_type=BlockType.Header)

            page.add_box(header)
        if footer_boxes:
            footer = Block(top=min([item.top for item in footer_boxes]), left=0,
                           width=page.width, height=page.height - min([item.top for item in footer_boxes]),
                           block_type=BlockType.Footer)
            page.add_box(footer)

        for block in [b for b in page if isinstance(b, Block) and b.left != 0]:
            if block.overlaps(header) or block.overlaps(footer):
                page.delete_boxes(block)


def clean_ocr(document):
    """ Remove garbage from OCR. These are usually single characters with large font size either
    to the left or right of the page."""
    for page in document:
        to_remove = []
        for text in [b for b in page if isinstance(b, TextBox)]:
            text_clean = simple_tags.sub('', text.content.text).strip()
            if ((len(text_clean) == 1 and text.content.size > 25) or
                (len(text_clean) <= 3 and text.content.size < 6)) \
                    and (text.left < page.width * 0.1 or text.right > page.width * 0.9):
                to_remove.append(text)
        page.delete_boxes(to_remove)
