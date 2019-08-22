import sys
import re
import unicodedata

# Get all unicode characters
all_chars = (chr(i) for i in range(sys.maxunicode))
# Get all non printable characters
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# Create regex of above characters
control_char_re = re.compile('[{}]'.format(re.escape(control_chars)))


def remove_non_printable(input_string):
    return control_char_re.sub('', input_string)


def replace_unicode_characters(string):
    string = string.replace('&#8226;', '•')
    string = string.replace('&#61623;', '•')
    string = string.replace('&#163;', '£')
    string = string.replace('&#8211;', '–')
    string = string.replace('&#8220;|&#147;|&#93;', '“')
    string = string.replace('', '“')
    string = string.replace('&#8221;|&#148;|&#94;', '”')
    string = string.replace('', '”')
    string = string.replace('&#34;', '"')
    string = string.replace('&#8217;|&#146;|&#x92;|', '’')
    string = string.replace('', '’')
    string = string.replace('&amp;', '&')
    return string


def escape_characters_for_xml(string):
    string = string.replace('&', '&amp;')
    string = string.replace('"', '&quot;')
    string = string.replace('\'', '&apos;')
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    return string
