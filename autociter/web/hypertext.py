from autociter.web.webpages import Webpage
import html2text

ignored = {"Search", "News", "Home"}
def remove_text_before_first_header(string):
    index = 0
    while string[index:index + len("\n# ")] != "\n# " or string[index + len("\n# "):string.find("\n", index + len("\n# "))] in ignored:
        index += 1
    return string[index + 1:]

def get_top_of_text(string):
    return string[:350]

def get_bottom_of_text(string):
    return string[len(string) - 250:]

def remove_the_word_image(string):
    return string.replace("\n\nImage", "")

def get_content(url):
    html = Webpage(url).source
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    h.skip_internal_links = True
    h.ignore_anchors = True
    text = h.handle(html)
    text = remove_text_before_first_header(text)
    text = remove_the_word_image(text)
    return get_top_of_text(text), get_bottom_of_text(text)
