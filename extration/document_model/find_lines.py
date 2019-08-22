import itertools
from .document import Document, Interval


def increment(other, val=1):
    return other + val


def find_lines(document: Document, section: Interval):
    if len(document) <= section.end:
        raise ValueError("Section is longer than the document")

    """ return an interval for each line in header """
    string_indices = [token.index for token in document.get_section_tokens(section) if token.text == '\n']
    string_indices = [string_index for i, string_index in enumerate(string_indices) if
                      (i < len(string_indices) - 1 and string_indices[i + 1] - string_indices[i] > 1)
                      or (i == len(string_indices) - 1)]
    lines = list(itertools.starmap(Interval, zip(map(increment, string_indices[:-1]), string_indices[1:])))

    if not lines:
        return []

    # Add first line
    if lines[0].start > 0 and not (lines[0].start == 1 and document.tokens[0].text == '\n'):
        lines.insert(0, Interval(0, lines[0].start - 1))

    # Add what is remaining as last line
    if (len(section) - 1) - lines[-1].end > 1:
        lines.append(Interval(lines[-1].end + 1, section.end))

    # Remove line change from the end of lines
    for line in lines:
        if document.tokens[line.end].text == '\n':
            line.end = line.end - 1
    return lines
