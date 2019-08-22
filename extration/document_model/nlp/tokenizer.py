import spacy
import re

punctuation = r'(\.){2,} … …… \/ \$ \£ \ \¢ ® : ; \! \? ¿ ؟ ¡ \( \) \[ \] \{ \} < > _ # \* & 。 ？ ！ % 、 ； ： ～ · । ، ؛ ٪ \| \' \'\' " ” “ `` ` ‘ ´ ‘‘ ’’ „ » « 「 」 『 』 （ ） 〔 〕 【 】 《 》 〈 〉 ='
punctuation_list = '… …… / : ; \! ? ¿ ؟ ¡ ( ) [ ] { } < > _ # * & 。 % ？ |！ 、 ； ： ～ · । ، ؛ ٪ \' " ” “ `` ` ‘ ´ ‘‘ ’’ „ » « 「 」 『 』 （ ） 〔 〕 【 】 《 》 〈 〉- -'.split()

split_chars = lambda char: list(char.strip().split(' '))

latin_chars_small = re.compile('[ivx]+')
latin_chars_capital = re.compile('[IVX]+')
letters_small = re.compile('[a-z]{1,2}')
letters_capital = re.compile('[A-Z]{1,2}')
single_letter = re.compile('[a-zA-Z]')
quote_end = re.compile('(\'|’|‘)s$')


def compile_infix_regex(entries):
    expression = '|'.join([piece for piece in entries if piece.strip()])
    return re.compile(expression)


def fix_errors(doc):
    for i, token in enumerate(doc):
        if token.text in punctuation_list:
            token.tag_ = token.text
        if latin_chars_small.fullmatch(token.text) or latin_chars_capital.fullmatch(token.text):
            token.tag_ = 'LCD'
            if i < len(doc) - 1 and doc[i+1].text == ')':
                token.tag_ = 'LS'
        elif (letters_small.fullmatch(token.text) or letters_capital.fullmatch(token.text)) and i < len(doc) - 1 and doc[i+1].text == ')':
            token.tag_ = 'LS'
        elif single_letter.fullmatch(token.text) and token.tag_ in ['NN', 'NP', 'NNP', 'UH']:
            token.tag_ = 'CHAR'
        elif quote_end.match(token.text):
            token.tag_ = 'POS'
    return doc


def join_to_text(word_tokens: list, to_remove: list=None):
    text = ' '.join(word_tokens)
    text = re.sub('( )+', ' ', text).strip()
    text = re.sub('\'\'', '"', text)
    text = re.sub('``( )*', '"', text)
    for symbol in ['.', ',', ';', ':', ')', ']', '}', '\'\'', '\'']:  # Remove space before certain symbols
        text = re.sub('( )\{0}'.format(symbol), symbol, text)
    for symbol in ['(', '[', '{', ]:  # Remove space before certain symbols
        text = re.sub('\{0}( )'.format(symbol), symbol, text)
    text = re.sub('( )*\n( )*', ' ', text)

    if to_remove:
        for item in to_remove:
            text = re.sub(item, '', text)
    return text


infix_finditer = compile_infix_regex(split_chars(punctuation)).finditer

spacy_model = spacy.load('en', disable=['parser', 'ner'])
spacy_model.max_length = 10000000
spacy_model.add_pipe(fix_errors, last=True)
spacy_model.tokenizer = spacy.tokenizer.Tokenizer(spacy_model.vocab, prefix_search=spacy_model.tokenizer.prefix_search,
                                                  suffix_search=spacy_model.tokenizer.suffix_search,
                                                  infix_finditer=infix_finditer,
                                                  token_match=spacy_model.tokenizer.token_match)


def tokenize_text(text: str):
    return [(token.text, token.tag_, token.shape_)
            for token in spacy_model(text) if token.tag_ != '_SP']
