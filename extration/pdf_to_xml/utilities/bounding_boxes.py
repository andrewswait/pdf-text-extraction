TOLERANCE = 5


def do_overlap(bbox1, bbox2):
    """
    :param bbox1: bounding box of the first rectangle
    :param bbox2: bounding box of the second rectangle
    :return: 1 if the two rectangles overlap
    """
    if bbox1[2] < bbox2[0] or bbox2[2] < bbox1[0]:
        return False
    if bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1]:
        return False
    return True


def is_contained(bbox1, bbox2, tol=TOLERANCE):
    """
    :param bbox1: bounding box of the first rectangle
    :param bbox2: bounding box of the second rectangle
    :return: True if bbox1 is contaned in bbox2
    """
    if bbox1[0] > bbox2[0]-tol and bbox1[1] > bbox2[1]-tol:
        if bbox1[2] < bbox2[2]+tol and bbox1[3] < bbox2[3]+tol:
            return True
    return False


def merge_bounding_boxes(bbox1, bbox2):
    """
    :param bbox1: (top, left, bottom, right)
    :param bbox2: (top, left, bottom, right)
    :return: Merge bounding boxes
    """
    if is_contained(bbox1, bbox2):
        return bbox2
    elif is_contained(bbox2, bbox1):
        return bbox1
    else:
        return (min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3]))


def get_rectangles(vertical_lines, horizontal_lines):
    """
    :param vertical_lines: list of vertical lines coordinates
    :param horizontal_lines: list of horizontal lines coordinates
    :return: List of bounding boxes for tables
    """
    # TODO : add tolerance
    rectangles = []
    i = 0
    j = 0
    while i < len(horizontal_lines) and j < len(vertical_lines):
        if int(horizontal_lines[i][0]) == vertical_lines[j][0]:
            if int(horizontal_lines[i][1]) == int(vertical_lines[j][1]):
                h = horizontal_lines[i]
                v = vertical_lines[j]
                rectangles += [(h[0], h[1], v[2], h[3])]
                i += 1
                j += 1
            elif int(horizontal_lines[i][1]) < int(vertical_lines[j][1]):
                i += 1
            else:
                j += 1
        elif int(horizontal_lines[i][0]) < int(vertical_lines[j][0]):
            i += 1
        else:
            j += 1
    return rectangles


def get_outer_bounding_boxes(rectangles):
    """
    :param rectangles: list of bounding boxes (top, left, bottom, right)
    :return: outer bounding boxes (only the largest bbox when bboxes intersect)
    """
    if len(rectangles) == 0:
        return []
    to_remove = []
    for i, bbox1 in enumerate(rectangles):
        for j, bbox2 in enumerate(rectangles[i+1:]):
            if is_contained(bbox1, bbox2):
                to_remove.append(i)
                break
            elif is_contained(bbox2, bbox1):
                to_remove.append(i + j + 1)

    for i in sorted(set(to_remove), reverse=True):
        del rectangles[i]
    return rectangles


def get_intersection(bbox1, bbox2):
    """
    :param bbox1: (page, width, height, top, left, bottom, right)
    :param bbox2: (page, width, height, top, left, bottom, right)
    :return: intersection if bboxes are in the same page and intersect
    """
    intersection = None
    top_1, left_1, bottom_1, right_1 = bbox1
    top_2, left_2, bottom_2, right_2 = bbox2
    if do_overlap((top_1, left_1, bottom_1, right_1), (top_2, left_2, bottom_2, right_2)):
        intersection = [max(top_1, top_2), max(left_1, left_2), min(bottom_1, bottom_2), min(right_1, right_2)]
    return intersection


def get_union(bbox1, bbox2):
    """
    :param bbox1: (page, width, height, top, left, bottom, right)
    :param bbox2: (page, width, height, top, left, bottom, right)
    :return: intersection if bboxes are in the same page and intersect
    """
    intersection = None
    top_1, left_1, bottom_1, right_1 = bbox1
    top_2, left_2, bottom_2, right_2 = bbox2
    if do_overlap((top_1, left_1, bottom_1, right_1), (top_2, left_2, bottom_2, right_2)):
        intersection = [min(top_1, top_2), min(left_1, left_2), max(bottom_1, bottom_2), max(right_1, right_2)]
    return intersection


def compute_iou(bbox1, bbox2):
    """
    :param bbox1: (page, width, height, top, left, bottom, right)
    :param bbox2: (page, width, height, top, left, bottom, right)
    :return: intersection over union if bboxes are in the same page and intersect
    """
    top_1, left_1, bottom_1, right_1 = bbox1
    top_2, left_2, bottom_2, right_2 = bbox2
    if do_overlap((top_1, left_1, bottom_1, right_1), (top_2, left_2, bottom_2, right_2)):
        intersection = (min(bottom_1, bottom_2) - max(top_1, top_2))*(min(right_1, right_2) - max(left_1, left_2))
        union = (bottom_1-top_1)*(right_1-left_1) + (bottom_2-top_2)*(right_2-left_2) - intersection
        return float(intersection)/float(union)
    return 0.
