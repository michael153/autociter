from autociter.web.webpages import Webpage

IGNORED_HEADERS = {"Search", "News", "Home"}
IGNORED_SUBSTRINGS = {"Image\n\n"}


def get_content(markdown):
    start = find_title(markdown)
    content = markdown[start:]
    return clean(content)


def find_title(markdown):
    for heading_size in range(1, 7):
        search_start = 0
        while contains_heading(markdown, heading_size, search_start):
            heading_start = find_heading(markdown, heading_size, search_start)
            heading_text = get_heading_text(markdown, heading_start)
            if heading_text not in IGNORED_HEADERS:
                return heading_start
            search_start = heading_start + len(heading_text)
    return -1


def contains_heading(markdown, size=1, start=0):
    return find_heading(markdown, size, start) != -1

def find_heading(markdown, size=1, start=0):
    for index in range(start, len(markdown)):
        desired = "\n" + "#" * size + " "
        if markdown[index:index + len(desired)] == desired:
            return index + len("\n")
    return -1


def get_heading_text(markdown, heading_start=0):
    whitespace_index = markdown.find(" ", heading_start)
    newline_index = markdown.find("\n", whitespace_index)
    return markdown[whitespace_index + 1:newline_index]


def clean(content):
    for substring in IGNORED_SUBSTRINGS:
        content = content.replace(substring, "")
    return content
