import re
import nltk
from itertools import starmap, chain


sentence_pattern = re.compile(
    r"""
        (\n\W*\([A-z]{1,3}\))               # newline then one or more letters in brackets
        |
        (\n\W*\(([IVX]{1,4}|[ivx]{1,4})\))  # newline then one or more latin numerals in brackets
        |
        (\n\W*\([0-9]+\))                   # newline then one or more numbers in brackets
        |
        (\n\W+\n)                           # multiple blank lines
        |
        (\n([0-9]+\.)+)                     # one or more numbers and dots after a newline
        |
        (\n[IVX]{1,4}\.([0-9]{1,2}\.?)+)
        |
        ((\n([IVX]{1,4}|[ivx]{1,4})\.)+)    # latin numerals and dot after a newline
        |
        (\n([A-Z]\.)+)                      # A-Z and dot after a newline
    """,
    flags=re.DOTALL and re.VERBOSE
)

list_start = re.compile('(?:[:;]\s*)([A-z0-9]{1,2}|[IVX]{1,4}|[ivx]{1,4})\.$')

wrong_list_start = re.compile('\s*\([0-9\s]+\)\s*(day|month|year|calendar|working|business)', flags=re.IGNORECASE)

inline_list_start = re.compile('((.)*?:-?)(\s)+((\(*[a-z]+\)|-)(.|\s)*)')

inline_list_item = re.compile('(;|,|:)(and|or|\s)+((\(*[a-z]+\)|-))')

numbering = re.compile('\s*([A-z0-9]{1,2}|[IVX]{1,4}|[ivx]{1,4})\.')

paragraph_numbering = re.compile('\s*(\(*[0-9\s]+\.*\)*)+')

section_numbering = re.compile('(clause|section|article|chapter|part|schedule|annex|appendix|paragraph)(s)*'
                               '(\s+(([0-9\s]+\.*)+[\s,]+)+)*[^\.:;]{0,3}\s*', flags=re.IGNORECASE)

abbreviations = re.compile('(e\.g\.|i\.e\.|etc\.|a\.m\.|p\.m\.|approx\.|p\.a\.|encl\.|incl\.|ft\.|ave\.|est\.|art\.|sec\.)[,\s]*$',
                           flags=re.IGNORECASE)


def split_sentences(text: str):
    """
    Splits text in sentences
    :param text: text to split
    :return: List of intervals, one per sentence
    """
    # First split on patterns that are known to start sentences
    splits = sentence_pattern.finditer(text)
    indices = [0] + [split.start() for split in splits] + [len(text)]
    slices = starmap(slice, zip(indices, indices[1:]))

    # Split each of the resulting sentences further, using nltk
    sentences_text = [item.strip() for item in chain.from_iterable(nltk_sentence_split(text[slice_].replace('\n', ' ')) for slice_ in slices)]

    # Third passage to further split for some cases of lists that were not covered before. When : or ; are not after \n
    sentences_text_final = []
    for sentence in sentences_text:
        match = list_start.search(sentence)
        if match:
            sentences_text_final.append(sentence[:match.span(1)[0]])
            sentences_text_final.append(sentence[match.span(1)[0]:match.span(1)[1] + 1])
        else:
            sentences_text_final.append(sentence)

    # Find indices in original text for each sentence
    text = text.replace('\n', ' ')
    offset, previous_sentence = 0, ''
    sentences = []
    for sentence in sentences_text_final:
        start = text.find(sentence, offset)
        if start < 0:
            raise ValueError('Sentence not found: {}'.format(set))
        end = start + len(sentence)
        offset = end

        # Merge sentences that have been wrongly split. Merge in following cases
        # 1. It is a small sentence and it is not numbering, i.e. probably ending of previous sentence
        # 2. It is number and the previous sentence ends with section title, probably a reference to section in the text
        # 3. Previous sentence is very small.
        # 4. Previous sentence is an abbreviation, i.e. wrongly split because of full stops.
        if sentences and (wrong_list_start.match(sentence)
                          or (len(sentence) <= 10 and not numbering.fullmatch(sentence))
                          or (paragraph_numbering.match(sentence) and section_numbering.search(previous_sentence)
                              and sentence.endswith(list(section_numbering.finditer(previous_sentence))[-1].group(0)))                          or len(previous_sentence) <= 10
                          or abbreviations.search(previous_sentence)):
            sentences[-1][1] = end
            sentences[-1][2] += ' ' + sentence
            previous_sentence = sentences[-1][2]
        else:
            sentences.append([start, end, sentence])
            previous_sentence = sentence

    # Fourth splitting pass for cases where a list is in-line in the sentence, i.e. no line breaks in front of numbering
    # e.g. The supplier shall: a) .....; b) ..... etc
    final_sentences, open_list = [], False
    for sentence in sentences:
        list_match = inline_list_start.search(sentence[2])
        if list_match:  # Try detect inline list start
            open_list = True
            start, end, sentence_text = sentence[0], sentence[1], sentence[2]

            # Add list start, e.g. "The supplier shall:" as a separate sentence
            final_sentences.append([start, start + list_match.regs[1][1], sentence_text[:list_match.regs[1][1] + 1]])

            # Match list items, e.g. a) ...., in the remaining text
            local_start = 0
            start = start + list_match.regs[4][0]  # Start of first item of list within the whole document
            items_text = sentence_text[list_match.regs[4][0]:]  # Remaining string containing the lsit
            for m in inline_list_item.finditer(items_text):
                end, local_end = start + m.regs[2][0], m.regs[2][0]
                final_sentences.append([start, end, items_text[local_start:local_end]])
                start = end
                local_start = local_end if items_text[local_end] != ' ' else local_end + 1

            if local_start < len(items_text):
                final_sentences.append([start, sentence[1], items_text[local_start:]])
        elif open_list:  # If the previous sentence was an inline list try to see if this one is the continuation
            start, end, sentence_text = sentence[0], sentence[1], sentence[2]

            m, local_start = None, 0
            for m in inline_list_item.finditer(sentence_text):
                end, local_end = start + m.regs[2][0], m.regs[2][0]
                final_sentences.append([start, end, sentence_text[local_start:local_end]])
                start = end
                local_start = local_end if sentence_text[local_end] != ' ' else local_end + 1

            if local_start < len(sentence_text):
                final_sentences.append([start, sentence[1], sentence_text[local_start:]])

            if m is None:
                open_list = False
        else:
            final_sentences.append(sentence)

    return final_sentences


def nltk_sentence_split(text: str):
    if text:
        sentences = nltk.sent_tokenize(text)
        if sentences and len(sentences) > 1 and len(sentences[0]) <= 10:
            first_sent = sentences[0]
            sentences = sentences[1:]
            if re.fullmatch('[\s\.]+', first_sent):
                return sentences
            else:
                for m in re.finditer('{}(\s+){}'.format(re.escape(first_sent), re.escape(sentences[0])), text):
                    sentences[0] = first_sent + m.group(1) + sentences[0]
                    break
        return sentences
    else:
        return []

