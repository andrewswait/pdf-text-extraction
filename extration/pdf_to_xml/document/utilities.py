import os
from .document import Document, TextBox, Block, ImageBox, BlockType
from extration.pdf_to_xml.utilities import create_path, create_file_path
from extration.pdf_to_xml.utilities.character_replace import escape_characters_for_xml, remove_non_printable


def convert_to_html(document_model: Document, output_file=None):
    image_folder = os.path.splitext(output_file)[0]

    text_content = ['<html>', '<head>', '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
                    '</head>', '<body>']
    for no, page in enumerate(document_model):
        text_content.append('<div style="position:relative;border-bottom:{};width:{}px;height:{}px">'.format(
            '1px solid rgba(0, 0, 0, 0.1)',
            page.width, page.height
        ))
        for block in [item for item in page if not isinstance(item, TextBox)]:
            if isinstance(block, Block):
                text_content.append(
                    '<div style="position:absolute;border:{};top:{}px;left:{}px;width:{}px;height:{}px">'.format(
                        '1px solid rgba(0, 0, 0, 0.1)',
                        block.top, block.left,
                        block.width, block.height
                    ))
                for box in page.get_contained_text_boxes(block):
                    if remove_non_printable(box.content.text).isspace() \
                            or remove_non_printable(box.content.text) == '':
                        continue
                    text = make_text_content(box)

                    text_content.append(
                        '<span style="position:absolute;top:{}px;left:{}px;width:{};height:{}px;font-family:{};font-size:{}px">{}</span>'.format(
                            box.top - block.top, box.left - block.left, box.width, box.height,
                            box.content.font, box.content.size,
                            remove_non_printable(text)
                        ))
                text_content.append('</div>')
            elif isinstance(block, ImageBox):
                create_path(image_folder)
                with open(os.path.join(image_folder, os.path.basename(block.file_name)), 'wb+') as file:
                    file.write(block.file_stream)
                if block.top < 50 and (page.height - block.height < 50 or page.width - block.width < 50):
                    continue

                text_content.append(
                    '<div style="position:absolute;top:{}px;left:{}px;width:{}px;height:{}px">'.format(
                        block.top, block.left,
                        block.width, block.height
                    ))
                text_content.append('<img src="{}" style="width:{}px;height:{}px"></img>'.format(
                    os.path.join(image_folder, os.path.basename(block.file_name)),
                    block.width, block.height
                ))
                text_content.append('</div>')
        text_content.append('</div>')

    text_content.extend(['</body>', '</html>'])
    text_content = ''.join(text_content)

    if output_file:
        create_file_path(output_file)
        with open(output_file, 'w+', newline='\n', encoding='utf-8') as output_fd:
            output_fd.write(text_content)

    return text_content


def convert_to_xml(document_model: Document, output_file=None, tool='pdftohtml', is_ocr=False):
    if output_file is not None:
        image_folder = os.path.splitext(output_file)[0]

    text_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<content version="2.0" extractor="{}">'.format(tool)]
    for no, page in enumerate(document_model):
        text_content.append('<page number="{}" height="{}" width="{}">'.format(
            page.number, page.height, page.width
        ))
        for block in [item for item in page if not isinstance(item, TextBox)]:
            if isinstance(block, Block) and block.type != BlockType.Footer and block.type != BlockType.Header:
                text_content.append(
                    '<text_block top="{}" left="{}" width="{}" height="{}">'.format(
                        block.top, block.left,
                        block.width, block.height
                    ))
                for box in page.get_contained_text_boxes(block):
                    if remove_non_printable(box.content.text).isspace() \
                            or remove_non_printable(box.content.text) == '':
                        continue
                    text = make_text_content(box)
                    text_content.append(
                        '<text top="{}" left="{}" font="{}" size="{}">{}</text>'.format(
                            box.top, box.left, box.content.font, box.content.size,
                            remove_non_printable(text)
                        ))
                text_content.append('</text_block>')
            elif isinstance(block, ImageBox):
                if is_ocr and block.top < 50 and (page.height - block.height < 50 or page.width - block.width < 50):
                    continue
                if block.file_id is None:
                    if output_file is None:
                        continue
                    create_path(image_folder)
                    with open(os.path.join(image_folder, os.path.basename(block.file_name)), 'wb+') as file:
                        file.write(block.file_stream)
                    source = os.path.join(image_folder, os.path.basename(block.file_name))
                else:
                    source = block.file_id

                text_content.append('<image_block src="{}" top="{}" left="{}" width="{}" height="{}">'.format(
                    source,
                    block.top, block.left,
                    block.width, block.height
                ))
                text_content.append('</image_block>')

        text_content.append('</page>')

    text_content.extend(['</content>'])
    text_content = ''.join(text_content)

    if output_file:
        create_file_path(output_file)
        with open(output_file, 'w+', newline='\n', encoding='utf-8') as output_fd:
            output_fd.write(text_content)

    return text_content


def make_text_content(box: TextBox):
    if box.content.emphasis is None:
        return box.content.text

    text, stack = [], []
    for i, e in enumerate(box.content.emphasis):
        if 'b' in box.content.emphasis[i] and (i == 0 or 'b' not in box.content.emphasis[i - 1]):
            text.append('<b>')
            stack.append('b')
        if 'i' in box.content.emphasis[i] and (i == 0 or 'i' not in box.content.emphasis[i - 1]):
            text.append('<i>')
            stack.append('i')
        text.append(escape_characters_for_xml(box.content.text[i]))
        if 'i' in box.content.emphasis[i] and (
                i == len(box.content.emphasis) - 1 or 'i' not in box.content.emphasis[i + 1]):
            if stack.pop() != 'i':
                text.extend(['</b>', '</i>', '<b>'])
                stack.append('b')
            else:
                text.append('</i>')
        if 'b' in box.content.emphasis[i] and (
                i == len(box.content.emphasis) - 1 or 'b' not in box.content.emphasis[i + 1]):
            if stack.pop() != 'b':
                text.extend(['</i>', '</b>', '<i>'])
                stack.append('i')
            else:
                text.append('</b>')

    return ''.join(text)
