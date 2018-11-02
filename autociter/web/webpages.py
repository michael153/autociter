# Copyright 2018 Balaji Veeramani, Michael Wan
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Author: Balaji Veeramani <bveeramani@berkeley.edu>
"""Define Webpage and WikipediaArticle objects."""
from urllib import request
import html2text


class Webpage:
    """A generic webpage."""

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "Webpage('{0}')".format(self.url)

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if not isinstance(other, Webpage):
            return False
        return self.url == other.url

    @property
    def source(self):
        """Return the source code of a webpage."""
        client = request.urlopen(self.url)
        bytecode = client.read()
        return bytecode.decode("utf-8", "replace")

    @property
    def markdown(self):
        """Return the source code of a webpage in markdown formatting."""
        parser = html2text.HTML2Text()
        parser.ignore_images = True
        parser.ignore_links = True
        return parser.handle(self.source).rstrip()

    @property
    def content(self):
        IGNORED_HEADERS = {"Search", "News", "Home"}
        IGNORED_SUBSTRINGS = {"Image\n\n"}

        def find_title(markdown):
            for heading_size in range(1, 7):
                search_start = 0
                while contains_heading(markdown, heading_size, search_start):
                    heading_start = find_heading(markdown, heading_size,
                                                 search_start)
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

        start = find_title(self.markdown)
        content = self.markdown[start:]
        return clean(content)


class WikipediaArticle(Webpage):
    """A Wikipedia article.

    Each article has a corresponding page where users can edit the content of
    the article. In this page, users can see the Wikipedia-style citations (for
    example, {{cite web | ... | ... | ... }}).
    """

    def __init__(self, url):
        Webpage.__init__(self, url)
        self.title = url[url.find("/wiki/") + len("/wiki/"):]
        edit_url = "https://en.wikipedia.org/w/index.php?title=" + self.title + "&action=edit"
        self.edit_page = Webpage(edit_url)

    def __repr__(self):
        return "WikipediaArticle('{0}')".format(self.url)

    def __str__(self):
        return self.title
