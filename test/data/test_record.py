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
import unittest

from autociter.data.storage import Record


class ArticleTest(unittest.TestCase):

    def testGetItem(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("Bob Ross", r["author"])

    def testGetItem_noValue(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("", r["url"])

    def testContains(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertTrue("title" in r)

    def testContains_nonexistantField(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertFalse("url" in r)

    def testEquals_sameValues(self):
        r1 = Record(["title", "author"], ["Painting", "Bob Ross"])
        r2 = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual(r1, r2)

    def testEquals_differentValues(self):
        r1 = Record(["title", "author"], ["Painting", "Bob Ross"])
        r2 = Record(["title", "author"], ["Food", "Gordon Ramsay"])
        self.assertNotEqual(r1, r2)

    def testCsv(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("Painting\tBob Ross", r.__csv__())


    def testRepr(self):
        r = Record(["title"], ["Flyff"])
        self.assertEqual("Record(['title'], ['Flyff'])", repr(r))

    def testStr(self):
        r = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("title\tPainting\nautho\tBob Ross", str(r))
