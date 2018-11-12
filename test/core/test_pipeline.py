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
import autociter.core.pipeline as pipeline


# pylint: disable=missing-docstring
class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.mock_data_dir = assets.MOCK_DATA_PATH + "/pipeline/"

    def test_get_text_from_url_pdf(self):
        with open(self.mock_data_dir + "pdf_url_list", "r") as datafile:
            urls = datafile.read().split('\n')
            bools = []
            for url in urls:
                bools.append(pipeline.get_text_from_url(url) != "")
            self.assertEqual(all(bools), True)

    def test_get_text_from_url_regular(self):
        with open(self.mock_data_dir + "regular_url_list", "r") as datafile:
            urls = datafile.read().split('\n')
            bools = []
            for url in urls:
                bools.append(pipeline.get_text_from_url(url) != "")
            self.assertEqual(all(bools), True)

    def test_get_wiki_links(self):
        args_permutations = [[
            "title", "author", "publisher", "date", "url", "archive-url"
        ], ["author", "date", "url"], ["date", "url"], ["title"]]
        respective_lengths = [2, 4, 5, 5]
        bools = []
        for i, args in enumerate(args_permutations):
            length = respective_lengths[i]
            data = pipeline.get_wiki_article_links_info(
                self.mock_data_dir + "mock_wiki_links", args)
            bools.append(list(data[1].keys()) == args)
            bools.append(len(data[0]) == length)
        self.assertEqual(all(bools), True)

    def test_clean_text(self):
        texts = [
            "(October 6th, 2000)", "(Hi my name is\nMichael)",
            "_What _in _the _world... hi", "Jean-Jacques Rousseau",
            "'I'm so happy!,' said '''VIRGIL ABLOH'''", "Califørniå",
            "Mr. @michaelwan__ is boys w/ Mrs. @middleclass.brian"
        ]
        answers = [
            "October 6th 2000", "Hi my name is\nMichael",
            "What in the world hi", "Jean Jacques Rousseau",
            "Im so happy said VIRGIL ABLOH", "Califørniå",
            "Mr michaelwan is boys w Mrs middleclass brian"
        ]
        bools = []
        for text, ans in zip(texts, answers):
            bools.append(pipeline.clean_text(text) == ans)
        self.assertEqual(all(bools), True)

    def test_find_attr_substr(self):
        texts = [
            "Hello my name is Michael Wan", "The date is April 13, 2000",
            "How many dates are in this sentence October 6th 2000, January 1st 1999",
            "BIRD is the word"
        ]
        datatypes = [("author", "Michael Wan"), ("date", "04/13/00"),
                     ("date", "10/06/00"), ("author", "bird")]
        outputs = [(17, 28), (12, 26), (36, 52), (-1, -1)]
        bools = []
        for text, datatype, true_output in zip(texts, datatypes, outputs):
            output = pipeline.find_attr_substr(text, datatype[1], datatype[0])
            bools.append(output == true_output)
        self.assertEqual(all(bools), True)

    # def test_locate_attributes(self):

    def test_word_vectorization(self):
        words = ['hello', 'michaelwan2000']
        words.append(''.join(
            random.choice('0123456789ABCDEF ') for i in range(500)))
        words.append(''.join(
            random.choice('0123456789ABCDEF ') for i in range(800)))
        bools = []
        for word in words:
            word = pipeline.slice_text(word)
            vectorized = pipeline.vectorize_text(word)
            unvectorized = pipeline.unvectorize_text(vectorized)
            hashed = pipeline.hash_vectorization(vectorized)
            unhashed = pipeline.unhash_vectorization(hashed)
            bools.append(len(word) == 600)
            bools.append(unvectorized == word)
            bools.append(unhashed == vectorized)
        self.assertEqual(all(bools), True)
