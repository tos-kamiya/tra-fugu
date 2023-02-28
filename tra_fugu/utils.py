def paragraph_iter(text):
    lines = text.split('\n')
    lines.append('')  # sentinel

    paragraph = []
    for L in lines:
        if L:
            paragraph.append(L)
            continue  # for L

        if paragraph:
            yield paragraph
            paragraph = []

    if paragraph:
        yield paragraph
        paragraph = []
