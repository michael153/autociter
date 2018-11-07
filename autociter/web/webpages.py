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
from autociter.utils.decorators import timeout

import html2text


class Webpage:
    """A generic webpage."""

    def __init__(self, url):
        self.url = url
        self.cache = {}

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
        if "source" in self.cache:
            return self.cache["source"]
        client = request.urlopen(self.url)
        bytecode = client.read()
        self.cache["source"] = bytecode.decode("utf-8", "replace")
        return self.cache["source"]

    @property
    def markdown(self):
        """Return the text of a webpage in markdown formatting."""
        if "markdown" in self.cache:
            return self.cache["markdown"]
        parser = html2text.HTML2Text()
        parser.ignore_images = True
        parser.ignore_links = True
        self.cache["markdown"] = parser.handle(self.source).rstrip()
        return self.cache["markdown"]

    @property
    @timeout(15)
    def content(self):
        """Retrieve the content of a webpage as markdown.

        This method identifies the relevant content in a webpage by searching
        the markdown for a heading and then returning all of the text after the
        heading. The algorithm works on the assumption that the title of an
        article is the first large heading and that all relevant information
        occurs after the title.
        """
        if self.cache.get("content"):
            return self.cache["content"]
        ignored_headers = {"Search", "News", "Home"}
        ignored_substrings = {"Image\n\n"}

        def find_title(markdown):
            for heading_size in range(1, 7):
                search_start = 0
                while contains_heading(markdown, heading_size, search_start):
                    heading_start = find_heading(markdown, heading_size,
                                                 search_start)
                    heading_text = get_heading_text(markdown, heading_start)
                    if heading_text not in ignored_headers:
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
            for substring in ignored_substrings:
                content = content.replace(substring, "")
            return content

        start = find_title(self.markdown)
        content = self.markdown[start:]
        self.cache["content"] = clean(content)
        return self.cache["content"]


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
