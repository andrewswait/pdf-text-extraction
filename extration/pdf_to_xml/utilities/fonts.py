from math import ceil, floor


def font_mapping(font_name:str):
    if 'Arial' in font_name:
        return 'Arial'
    elif 'TimesNewRoman' in font_name:
        return 'Times'
    elif 'Calibri' in font_name:
        return 'Calibri'
    elif 'AdvGulliv' in font_name:
        return 'AdvGulliv-R'
    else:
        font_name = font_name.replace('Bold', '')
        font_name = font_name.replace('-MT|MT', '')
        font_name = font_name.replace('-', '')
        return font_name


def round_with_middle(number):
    if number % 1 < 0.35:
        return floor(number)
    elif number % 1 > 0.65:
        return ceil(number)
    else:
        return floor(number) + 0.5
