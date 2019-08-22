import re

level_0 = re.compile('[^A-Z0-9a-z]*(article|section|clause|part)')
level_1 = re.compile('[^A-Z0-9a-z]*(I\.)*[0-9]{1,2}\.* ')
level_2 = re.compile('[^A-Z0-9a-z]*(I\.)*[0-9]{1,2}\.[0-9]{1,2}\.* ')
level_3 = re.compile('[^A-Z0-9a-z]*(I\.)*[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}\.* ')
list_letters = re.compile('[^A-Z0-9a-z]*\([a-hj-uwyzA-HJ-UWYZ]\)')
list_letters_lower = re.compile('[^A-Z0-9a-z]*\([[a-hj-uwyz]\)')
list_letters_lower_semi = re.compile('(\s)*[[a-hj-uwyz]\)')
list_letters_lower_dot = re.compile('(\s)*[[a-hj-uwyz]\.')
list_letters_upper = re.compile('[^A-Z0-9a-z]*\([A-HJ-UWYZ]\)')
list_letters_upper_semi = re.compile('(\s)*[A-HJ-UWYZ]\)')
list_letters_upper_dot = re.compile('(\s)*[A-HJ-UWYZ]\.')
list_latin = re.compile('[^A-Z0-9a-z]*\([ivx]{1,5}\)')
list_numbers = re.compile('[^A-Z0-9a-z]*\([0-9]{1,2}\)')


def search_paragraphs_by_pattern(sentences, pattern):
    if not sentences:
        return None
    matches = [i for i, item in enumerate(sentences) if pattern.match(item[2])]
    if len(matches) > 1 and matches[0] == 0:
        matches = list({0, *matches, len(sentences)})
        matches.sort()
        return [(sentences[i][0], sentences[j - 1][1], pattern.match(sentences[i][2]).group(0).strip())
                for i, j in zip(matches[:-1], matches[1:])]
    else:
        return None


def find_paragraphs(sentences):
    """
    Groups sentences into paragraphs
    :param sentences: list of tuples (start, end, text). The sentence indices are on tokens
    :return: List of tuples (start, end, numbering). The indices are on tokens and numbering is a string
    """
    if len(sentences) == 0:
        return []
    patterns = [level_1, level_2, level_3, list_letters_lower, list_letters_upper, list_letters_lower_semi,
                list_letters_upper_semi, list_latin, list_numbers, list_letters_lower_dot, list_letters_upper_dot]
    for pattern in patterns:
        paragraphs = search_paragraphs_by_pattern(sentences, pattern)
        if paragraphs:
            return paragraphs

    return [(sentences[0][0], sentences[-1][1], '')]
