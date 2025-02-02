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
"""Define objects that extract information from Wikipedia."""
from autociter.web.webpages import WikipediaArticle
from autociter.core.citations import WikipediaCitation


# pylint: disable=too-few-public-methods
class ElementExtractor:
    """An object that assists with data extraction.

    Extractor and its subclasses contain an extract method. The extract method
    takes a string and extracts substrings that are exclusively enclosed by
    the strings beg and end, which are defined in the __init__ method.

    The extract method may return the substrings as-is, or convert the strings
    to some other object. In either case, a list is returned.

    >>> e = Extractor("<p>", "</p>")
    >>> e.extract("<h1>Header</h1><p>Paragraph</p>")
    ["<p>Paragraph</p>"]
    """

    def __init__(self, beg, end):
        self.beg = beg
        self.end = end
        # By default, all results are valid.
        self.validate = lambda result: True

    def extract(self, string):
        """Return valid substrings enclosed by beg and end."""
        results = []
        left, right, rest = 0, 0, string
        while self.beg in rest and self.end in rest:
            left = string.find(self.beg, right) + len(self.beg)
            right = string.find(self.end, left) + len(self.end)
            start, end = left, right - len(self.end)
            results += [string[start:end]]
            rest = string[right:]
        return [r for r in results if self.validate(r)]


class WikipediaCitationExtractor(ElementExtractor):
    """Extracts citations defined in Wikipedia articles.

    Wikipedia article citations are denoted by the opening and closing tags
    "{{cite" and "}}", respectively. These references can be scraped from
    the edit-page of any Wikipedia article.
    """

    VARIANTS = ("{{cite", "{{Cite")

    def __init__(self, beg="{{cite"):
        ElementExtractor.__init__(self, beg, "}}")

    def extract(self, string):
        """Return references found in an article as Reference objects.

        Arguments:
            string: The source code of an edit-article webpage.
        """
        citations = ElementExtractor.extract(self, string)
        return [WikipediaCitation(c) for c in citations]


class WikipediaArticleExtractor(ElementExtractor):
    """Extracts Wikipedia articles."""

    # Special article types
    IGNORED_NAMESPACES = [
        "User:", "Wikipedia:", "File:", "MediaWiki:", "Template:", "Help:",
        "Category:", "Portal:", "Book:", "Draft:", "TimedText:", "Module:",
        "Gadget:", "Special:", "Main_Page", "Talk:", "User_talk:",
        "Wikipedia_talk:", "File_talk:", "MediaWiki_talk:", "Template_talk:",
        "Help_talk:", "Category_talk:", "Portal_talk:", "Book_talk:",
        "Draft_talk:", "TimedText_talk:", "Module_talk:", "Gadget_talk:",
        "Gadget_definition_talk:", "Media:"
    ]

    def __init__(self):
        ElementExtractor.__init__(self, "<a href=\"/wiki/", "\"")

        def validate(result):
            for prefix in self.IGNORED_NAMESPACES:
                if prefix in result:
                    return False
            return True

        # A result is invalid if the result represents a special article.
        self.validate = validate

    def extract(self, string):
        """Return articles found in a article as WikipediaArticle objects.

        The extract method searches an article's source code for references to
        other Wikipedia articles and returns them as WikipediaArticle objects. Special
        articles (e.g. Wikipedia help articles) are excluded.

        Arguments:
            string: The source code of an article. The article can be a catalog
                    of other articles (e.g. the "featured articles" article.)
        """
        titles = ElementExtractor.extract(self, string)
        return [
            WikipediaArticle("https://en.wikipedia.org/wiki/" + t)
            for t in titles
        ]
