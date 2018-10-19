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
"""Define Webpage and Article objects."""
from urllib import request

from crawlers import ArticleCrawler


class Webpage:
    """A generic webpage."""

    def __init__(self, url):
        """Initialize a Webpage instance.

        url must be a string with the prefix "https://".

        Arguments:
            url: The webpage's url
        """
        self.url = url
        client = request.urlopen(url)
        bytecode = client.read()
        self.source = bytecode.decode("utf-8", "replace")

    def __repr__(self):
        return "Webpage('{0}')".format(self.url)

    def __str__(self):
        return self.url


class Article(Webpage):
    """A Wikipedia article."""

    def __init__(self, url):
        Webpage.__init__(self, url)
        self.title = url[url.find("/wiki/") + len("/wiki/"):]
        edit_url = "https://en.wikipedia.org/w/index.php?title=" + self.title + "&action=edit"
        self.edit = Webpage(edit_url)

    def __repr__(self):
        return "Article('{0}')".format(self.url)

    @property
    def references(self):
        """Compute and return this article's citations as Reference objects.

        An article's citations are computed once, when the references method is first
        called. Thereafter, the references method is unused, as it is replaced by the
        references instance attribute.
        """
        self.references = ArticleCrawler().scrape(self)
        return self.references
