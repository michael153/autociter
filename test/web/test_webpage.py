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
"""Test methods of the Webpage object defined in web.webpages."""
import unittest

from test import server
import assets

from autociter.web.webpages import Webpage


# pylint: disable=invalid-name, missing-docstring
class WebpageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        server.start()

    def setUp(self):
        self.url = server.ADDRESS + "/simple_webpage.html"

    def testUrl(self):
        w = Webpage(self.url)
        self.assertEqual(w.url, self.url)

    def testRepr(self):
        w = Webpage(self.url)
        self.assertEqual("Webpage('" + self.url + "')", repr(w))

    def testStr(self):
        w = Webpage(self.url)
        self.assertEqual(self.url, str(w))

    def testEquals(self):
        w1 = Webpage(self.url)
        w2 = Webpage(self.url)
        self.assertEqual(w1, w2)

    def testSource(self):
        w = Webpage(self.url)
        filename = assets.path + "/test/simple_webpage.html"
        with open(filename) as source:
            self.assertEqual(w.source, source.read())

    def testMarkdown(self):
        w = Webpage(self.url)
        self.assertEqual("# Heading\n\nThis is a paragraph.", w.markdown)

    @classmethod
    def tearDownClass(cls):
        server.end()
