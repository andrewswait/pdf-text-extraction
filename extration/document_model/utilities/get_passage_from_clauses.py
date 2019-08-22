import re


def get_sections_by_type(section_type, clauses):
    if not section_type:
        return list(filter(lambda clause: clause.level == 0 or clause.level == 1, clauses))
    return list(filter(lambda clause: (section_type in clause.type) and (clause.level == 0 or clause.level == 1), clauses))


def get_subsections(parent_section, sections):
    found_sections = list(filter(lambda section: section.parent == parent_section.index, sections))
    return found_sections if len(found_sections) else list()


def get_content_from_children(parent_idx, structure):
    content = []
    for item in structure:
        if item.parent == parent_idx:
            content.append(item.header + ' ' + item.content)
    return content


def get_passage_from_clauses(sections, clause_types, level1_keywords, level2_keywords, level3_keywords):
    level1_keywords_regex = '|'.join(level1_keywords) if level1_keywords and len(level1_keywords) else None
    level2_keywords_regex = '|'.join(level2_keywords) if level2_keywords and len(level2_keywords) else None
    level3_keywords_regex = '|'.join(level3_keywords) if level3_keywords and len(level3_keywords) else None
    related_types = []
    for item in clause_types:
        related_types += get_sections_by_type(item, sections)
    if not len(related_types):
        related_types = get_sections_by_type(None, sections)
    level1_matched_sections = list(filter(lambda related_type: level1_keywords_regex is not None and re.search(level1_keywords_regex, related_type.name) is not None, related_types))
    results = []
    for level1_item in level1_matched_sections:
        subsections = get_subsections(level1_item, sections)
        for level2_item in subsections:
            if level2_keywords_regex and re.search(level2_keywords_regex, level2_item.name, re.IGNORECASE) is not None:
                sub_subsections = get_subsections(level2_item, sections)
                if not sub_subsections and level2_item.level > 1:
                    content = level2_item.content if len(level2_item.content) else '\n'.join(get_content_from_children(level2_item.index, sections))
                    results.append({'name': level2_item.name, 'content': content, 'idx': level2_item.content_idx})
                level3_found = False
                for level3_item in sub_subsections:
                    if level3_item.level > 1 and level3_keywords_regex and re.search(level3_keywords_regex, level3_item.name, re.IGNORECASE) is not None and len(level3_item.content):
                        results.append({'name': level3_item.name, 'content': level3_item.content, 'idx': level3_item.content_idx})
                        level3_found = True
                if not level3_found and level2_item.level > 1:
                    results.append({'name': level2_item.name, 'content': content, 'idx': level2_item.content_idx})
    return results


def get_monetary_value(text):
    current_regex = '(\u00a3|gbp|\\$|usd|\u20ac|eur|euro|euros)'
    number_regex = '[0-9]{1,5}(\.|,)*[0-9]{0,5}(\.|,)*[0-9]{0,5}(\.|,)*[0-9]{0,5}(billion|bn|mil|million){0,1}'
    currency_pos = re.search(current_regex, text, re.IGNORECASE)
    if currency_pos is None:
        return None
    text = text[currency_pos.start():]
    number_pos = re.search(number_regex, text, re.IGNORECASE)
    if number_pos is None:
        return None
    return text[0:number_pos.start()] + number_pos.group()


