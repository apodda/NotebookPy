def parse_title(text):
    if text != '':
        title = text.splitlines()[0]
    else:
        title = ''
    return title
