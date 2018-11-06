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
"""Test methods of the Record object defined in data.storage."""
import unittest

from autociter.data.storage import Record


# pylint: disable=missing-docstring
class WikipediaArticleTest(unittest.TestCase):

    def test_get_item(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("Bob Ross", record["author"])

    def test_get_item_with_no_value(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("", record["url"])

    def test_contains(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertTrue("title" in record)

    def test_contains_nonexistant_field(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertFalse("url" in record)

    def test_equals(self):
        record1 = Record(["title", "author"], ["Painting", "Bob Ross"])
        record2 = Record(["title", "author"], ["Painting", "Bob Ross"])
        record3 = Record(["title", "author"], ["Food", "Gordon Ramsay"])
        self.assertEqual(record1, record2)
        self.assertNotEqual(record1, record3)

    def test_csv(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("Painting\tBob Ross", record.__csv__("\t"))

    def test_repr(self):
        record = Record(["title"], ["Flyff"])
        self.assertEqual("Record(['title'], ['Flyff'])", repr(record))

    def test_str(self):
        record = Record(["title", "author"], ["Painting", "Bob Ross"])
        self.assertEqual("title\tPainting\nautho\tBob Ross", str(record))
