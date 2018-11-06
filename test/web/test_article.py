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
"""Test methods of the Article object defined in web.webpages."""
import unittest

from autociter.web.webpages import WikipediaArticle, Webpage


# pylint: disable=missing-docstring
class WikipediaArticleTest(unittest.TestCase):

    def test_title(self):
        article = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual("Chetro_Ketl", article.title)

    def test_edit_page(self):
        article = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        edit_page = Webpage(
            "https://en.wikipedia.org/w/index.php?title=Chetro_Ketl&action=edit"
        )
        self.assertEqual(edit_page, article.edit_page)

    def test_repr(self):
        article = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual(
            "WikipediaArticle('https://en.wikipedia.org/wiki/Chetro_Ketl')",
            repr(article))

    def test_str(self):
        article = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual("Chetro_Ketl", str(article))
