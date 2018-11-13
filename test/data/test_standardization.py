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
# Author: Michael Wan <m.wan@berkeley.edu>
"""Test methods defined in autociter.core.pipeline"""
import unittest
import random

import assets
import autociter.data.standardization as standardization


# pylint: disable=missing-docstring
class StandardizationTest(unittest.TestCase):
    # def setUp(self):
    # self.mock_data_dir = assets.MOCK_DATA_PATH + "/pipeline/"

    def test_std_text(self):
        texts_to_std = [
            "hello... my name is michael wan. bye!",
            "the date is April 13, 2000",
            "w.y.d - big boi? . hm",
            "'cripes', balaji veeramani",
            "(October 6th, 2000)", "(Hi my name is\nMichael)",
            "_What _in _the _world... hi", "Jean-Jacques Rousseau",
            "'I'm so happy!,' said '''VIRGIL ABLOH'''", "Califørniå",
            "mr. @michaelwan__ is boys w/ Mrs. @middleclass.brian"
        ]
        valid_outputs = [
            "Hello my name is michael wan bye",
            "The date is April 13 2000",
            "W y d big boi hm",
            "Cripes balaji veeramani",
            "October 6th 2000", "Hi my name is\nMichael",
            "What in the world hi", "Jean Jacques Rousseau",
            "Im so happy said VIRGIL ABLOH", "Califørniå",
            "Mr michaelwan is boys w Mrs middleclass brian"
        ]
        processed = [standardization.standardize(text, 'text') for text in texts_to_std]
        self.assertEqual(all([i == j for i, j in zip(valid_outputs, processed)]), True)

    def test_std_author(self):
        authors_test_cases = [
            ['John P. Lenin', 'Josiah De-Figuiera', 'J.J. Veeramani'],
            ['Gabby Shvartsman', 'PAUL BARRETTO'],
        ]
        valid_outputs = [
            ['John P Lenin', 'Josiah De Figuiera', 'Jj Veeramani'],
            ['Gabby Shvartsman', 'Paul Barretto']
        ]
        processed = [standardization.standardize(authors, 'author') for authors in authors_test_cases]
        self.assertEqual(all([i == j for i, j in zip(valid_outputs, processed)]), True)

    # def test_std_date(self):
    # def test_std_title(self):
    # def test_std_url(self):


    def test_find(self):
        texts = [
            "Hello my name is Michael Wan", "The date is April 13, 2000",
            "How many dates are in this sentence October 6th 2000, January 1st 1999",
            "BIRD is the word"
        ]
        datatypes = [("author", ["Michael Wan"]), ("date", "04/13/00"),
                     ("date", "10/06/00"), ("author", ["bird"])]
        outputs = [[(17, 28)], (12, 26), (36, 52), [(0, 4)]]
        bools = []
        for text, datatype, true_output in zip(texts, datatypes, outputs):
            output = standardization.find(datatype[1], text, datatype[0])
            bools.append(output == true_output)
        self.assertEqual(all(bools), True)
