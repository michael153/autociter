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


# pylint: disable=invalid-name, missing-docstring
class WikipediaArticleTest(unittest.TestCase):

    def testTitle(self):
        a = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual("Chetro_Ketl", a.title)

    def testEditPage(self):
        a = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        e = Webpage(
            "https://en.wikipedia.org/w/index.php?title=Chetro_Ketl&action=edit"
        )
        self.assertEqual(e, a.edit_page)

    def testRepr(self):
        a = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual(
            "WikipediaArticle('https://en.wikipedia.org/wiki/Chetro_Ketl')",
            repr(a))

    def testStr(self):
        a = WikipediaArticle("https://en.wikipedia.org/wiki/Chetro_Ketl")
        self.assertEqual("Chetro_Ketl", str(a))
