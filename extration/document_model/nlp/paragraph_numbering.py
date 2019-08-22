import re
from difflib import SequenceMatcher


def is_same_numbering_level(numbering1, numbering2):
    if re.search('(article|section|chapter|paragraph)', numbering1, flags=re.IGNORECASE) \
            and not re.search('(article|section|chapter|paragraph)', numbering2,flags=re.IGNORECASE):
            return False
    if re.search('(article|section|chapter|paragraph)', numbering2, flags=re.IGNORECASE) \
            and not re.search('(article|section|chapter|paragraph)', numbering1, flags=re.IGNORECASE):
            return False
    numbering1 = re.sub('(article|section|chapter|paragraph)', '', numbering1, flags=re.IGNORECASE)
    numbering2 = re.sub('(article|section|chapter|paragraph)', '', numbering2, flags=re.IGNORECASE)
    numbering1 = re.sub('( )*', '', numbering1)
    numbering2 = re.sub('( )*', '', numbering2)
    if is_full_text_numbering(numbering1) and is_full_text_numbering(numbering2):
        return True
    elif is_level_numbering(numbering1) and is_level_numbering(numbering2):
        return is_same_level_numbering(numbering1, numbering2)
    elif is_roman_numbering(numbering1) and is_roman_numbering(numbering2):
        return is_same_roman_numbering(numbering1, numbering2)
    elif is_letter_numbering(numbering1) and is_letter_numbering(numbering2):
        return True
    # Needs special attention cause roman numbering also tests positive as letter numbering
    # To avoid V. and a) classified as same level we also test for sequence distance
    elif is_brackets_numbering(numbering1) and is_brackets_numbering(numbering2) \
            and SequenceMatcher(None, numbering1, numbering2).ratio() >= 0.5:
        return is_same_brackets_numbering(numbering1, numbering2)
    if SequenceMatcher(None, numbering1, numbering2).ratio() > 0.5:
        return True
    return False


def is_same_type(numbering1, numbering2):
    if is_roman_numbering(numbering1) and is_roman_numbering(numbering2):
        return True
    if is_brackets_numbering(numbering1) and is_brackets_numbering(numbering2):
        return True
    if is_level_numbering(numbering1) and is_level_numbering(numbering2):
        return True
    return False


def contains_numbering(text):
    if is_roman_numbering(text):
        return True
    if is_brackets_numbering(text):
        return True
    if is_level_numbering(text):
        return True
    return False


def roman_numbers():
    return re.compile('(I|X|V){1,5}(\)|\.)*', flags=re.IGNORECASE)


def is_roman_numbering(text):
    if text is None or text == '':
        return False
    return re.match(roman_numbers(), text) is not None


def is_same_roman_numbering(text1, text2):
    if not (is_roman_numbering(text1) and is_roman_numbering(text2)):
        return False

    return len([x for x in text1.split('.') if x != '']) == len([x for x in text2.split('.') if x != ''])


def brackets_numbering():
    return re.compile('(\()*[a-z]((\))|(\.))', flags=re.IGNORECASE)

def full_text_numbering():
    return re.compile('(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN)', flags=re.IGNORECASE)

def is_letter_numbering(text):
    if text is None or text == '':
        return False
    return re.match(letter_numbering(), text) is not None

def letter_numbering():
    return re.compile('[A-Z]+(\.)*')


def is_brackets_numbering(text):
    if text is None or text == '':
        return False
    return re.match(brackets_numbering(), text)is not None

def is_full_text_numbering(text):
    if text is None or text == '':
        return False
    return re.match(full_text_numbering(), text)is not None


def is_same_brackets_numbering(text1, text2):
    if not (is_brackets_numbering(text1) and is_brackets_numbering(text2)):
        return False

    return len([x for x in text1.split('.') if x != '']) == len([x for x in text2.split('.') if x != ''])


def level_numbering():
    return re.compile('[0-9]+(\.)*[0-9]*(\.)*[0-9]*(\.)*', flags=re.IGNORECASE)


def is_level_numbering(text):
    """
    e.g. 1., 1.1., 1.1.1
    """
    if text is None or text == '':
        return False
    return re.match(level_numbering(), text) is not None


def is_same_level_numbering(text1, text2):
    if not (is_level_numbering(text1) and is_level_numbering(text2)):
        return False

    return len([x for x in text1.split('.') if x != '']) == len([x for x in text2.split('.') if x != ''])


def break_level_numbering(text):
    if is_level_numbering(text):
        return re.split('\.', text)
    else:
        return None
