from binascii import b2a_hex
import numpy
import scipy.ndimage
import cv2
import os
import struct


def image_to_bbox(contours):
    """
    x, y, w, h -> x1, y1 : x2, y2
    :param contours: list of contours in image coordinates
    :return:
    """
    for box in contours:
        box[2] = box[0] + box[2]
        box[3] = box[1] + box[3]
    return contours


def bbox_to_image(boxes):
    """
        x1, y1 : x2, y2 - > x, y, w, h
        :param contours: list of contours in bbox coordinates
        :return:
        """
    for box in boxes:
        box[2] = box[2] - box[0]
        box[3] = box[3] - box[1]
    return boxes


def find_contours(image):
    if isinstance(image, str):
        image = cv2.imread(image)

    # grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # get contours
    # for each contour found, draw a rectangle around it on original
    rectangles = []
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        rectangles.append([x, y, w, h])

    return rectangles


def draw_rectangles(image, rectangles, output_file=None, line_size=1):
    if isinstance(image, str):
        image = cv2.imread(image)

    for x, y, w, h in rectangles:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), line_size)

    # write original image with added contours to disk
    if output_file is not None:
        cv2.imwrite(output_file, image)


def gauss(img, dimension=10):
    kernel = numpy.ones((dimension, dimension)) / (dimension * dimension)
    return scipy.ndimage.convolve(img, kernel, mode='constant')


def save_image(lt_image, file_name, image_folder=None):
    """Try to save the image data from this LTImage object, and return the file name, if successful"""
    if not lt_image.stream:
        return None, None
    file_stream = lt_image.stream.get_rawdata()
    file_ext = determine_image_type(file_stream[0:4])

    if file_ext:
        file_name = '{}.{}'.format(file_name, file_ext)
    elif 'Filter' in lt_image.stream.attrs and hasattr(lt_image.stream.attrs, 'name')\
        and lt_image.stream.attrs['Filter'].name == 'CCITTFaxDecode':
        if 'K' in lt_image.stream.attrs['DecodeParms']:
            if lt_image.stream.attrs['DecodeParms']['K'] == -1:
                CCITT_group = 4
            else:
                CCITT_group = 3
        else:
            CCITT_group = 3
        width = lt_image.stream.attrs['Width']
        height = lt_image.stream.attrs['Height']
        img_size = len(file_stream)
        tiff_header = tiff_header_for_ccitt(width, height, img_size, CCITT_group)

        file_stream = tiff_header + file_stream
        file_name = '{}.{}'.format(file_name, 'tiff')
    else:
        return None, None

    if image_folder:
        with open(os.path.join(image_folder, file_name), 'wb+') as file:
            file.write(file_stream)
    return file_name, file_stream


def determine_image_type(stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
    if bytes_as_hex.startswith('ffd8'):
        file_type = 'jpeg'
    elif bytes_as_hex.startswith('89504e47'):
        file_type = 'png'
    elif bytes_as_hex.startswith('47494638'):
        file_type = 'gif'
    elif bytes_as_hex.startswith('49492A00') or bytes_as_hex.startswith('4D4D002A'):
        file_type = 'tiff'
    elif bytes_as_hex.startswith('424d'):
        file_type = 'bmp'
    return file_type


def tiff_header_for_ccitt(width, height, img_size, ccitt_group=4):
    tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
    return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, ccitt_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )
