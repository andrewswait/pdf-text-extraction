
def split_text_on_indices(text, indices):
    if not text or not indices:
        return []
    sub_strings = []
    previous_start = 0
    for idx in indices:
        sub_strings.append(text[previous_start:idx])
        previous_start = idx
    if previous_start < len(text):
        sub_strings.append(text[previous_start:len(text)])
    return sub_strings
