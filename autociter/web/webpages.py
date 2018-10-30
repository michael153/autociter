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
import html2text


class Webpage:
    """A generic webpage."""

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "Webpage('{0}')".format(self.url)

    def __str__(self):
        return self.url

    @property
    def source(self):
        """Return the source code of a webpage."""
        client = request.urlopen(self.url)
        bytecode = client.read()
        return bytecode.decode("utf-8", "replace")

    @property
    def markdown(self):
        """Return the source code of a webpage in markdown formatting.

        The markdown text is calculated once, when the source property is first
        called. Thereafter, the markdown is cached in the _source attribute.
        """
        parser = html2text.HTML2Text()
        parser.ignore_images = True
        parser.ignore_links = True
        parser.skip_internal_links = True
        parser.ignore_anchors = True
        return parser.handle(self.source)

class Article(Webpage):
    """A Wikipedia article."""

    def __init__(self, url):
        Webpage.__init__(self, url)
        self.title = url[url.find("/wiki/") + len("/wiki/"):]
        edit_url = "https://en.wikipedia.org/w/index.php?title=" + self.title + "&action=edit"
        self.edit = Webpage(edit_url)

    def __repr__(self):
        return "Article('{0}')".format(self.url)

    def __str__(self):
        return self.title
