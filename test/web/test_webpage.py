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


# pylint: disable=missing-docstring
class WebpageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        server.start()

    def setUp(self):
        self.url = server.ADDRESS + "/simple_webpage.html"

    def test_url(self):
        webpage = Webpage(self.url)
        self.assertEqual(webpage.url, self.url)

    def test_repr(self):
        webpage = Webpage(self.url)
        self.assertEqual("Webpage('" + self.url + "')", repr(webpage))

    def test_str(self):
        webpage = Webpage(self.url)
        self.assertEqual(self.url, str(webpage))

    def test_equals(self):
        webpage1 = Webpage(self.url)
        webpage2 = Webpage(self.url)
        self.assertEqual(webpage1, webpage2)

    def test_source(self):
        webpage = Webpage(self.url)
        filename = assets.WEBPAGES_PATH + "/simple_webpage.html"
        with open(filename) as source:
            self.assertEqual(webpage.source, source.read())

    def test_markdown(self):
        webpage = Webpage(self.url)
        self.assertEqual("# Heading\n\nThis is a paragraph.", webpage.markdown)

    @classmethod
    def tearDownClass(cls):
        server.end()
