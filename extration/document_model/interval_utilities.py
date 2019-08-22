from typing import Union, List
import re
from .interval import Interval
from .document import Token


paragraph_numbering = re.compile('[0-9]+(\.[0-9]+){0,2}')


def get_token_interval_from_char_interval(tokens: List[Token], character_interval: Interval) \
        -> Union[Interval, None]:
    """
    Returns the interval on the list of tokens that contains an interval on the characters of the test.
    Used to translate the output of a regular expression to indices on the tokens of that piece of text.
    :param tokens: Tokens of the text
    :param character_interval: interval on the ext as a string.
    :return: interval on the list of tokens
    """
    token_interval = Interval(0, 0)
    for item in tokens:
        if item.overlaps(character_interval):
            if token_interval.start == token_interval.end == 0:
                token_interval = Interval(item.index, item.index)
            else:
                token_interval.end = item.index
    if token_interval.start == token_interval.end == 0:
        return None
    return token_interval


def get_overlapped_tokens(tokens: List[Token], sequences: List[Interval]) -> Interval:
    """
    Returns an interval on the token lists that contains all the tokens for the beginning of the first sequence
    to the end of the last sequence
    :param tokens: Tokens of the text
    :param sequences: intervals on the list of tokens
    :return: single interval on the list of tokens
    """

    token_interval = Interval(min([s.start for s in sequences]), max([s.end for s in sequences]))
    # Get rid of special characters in the beginning
    while (tokens[token_interval.start].text in ['\n', ' ', ':', '-', ',', '.']
           or paragraph_numbering.match(tokens[token_interval.start].text)) \
            and token_interval.start < token_interval.end:
        token_interval.start += 1
    return token_interval
