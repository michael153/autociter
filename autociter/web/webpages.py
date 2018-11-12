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

# from timeout_decorator import timeout

from autociter.web.extractors import TitleFirstContentExtractor


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
    # @timeout(15)
    def content(self):
        """Return the predicted webpage content."""
        if "content" in self.cache:
            return self.cache["content"]
        extractor = TitleFirstContentExtractor(webpage=self)
        self.cache["content"] = extractor.content
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
