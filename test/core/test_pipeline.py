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

import assets
import random
import autociter.core.pipeline as pipeline

# pylint: disable=missing-docstring
class PipelineTest(unittest.TestCase):

    def setUp(self):
        self.mock_data_dir = assets.MOCK_DATA_PATH + "/pipeline/"

    # def test_get_text_from_url_pdf(self):
    #     urls = open(self.mock_data_dir + "pdf_url_list", "r").read().split('\n')
    #     bools = []
    #     for url in urls:
    #         bools.append(pipeline.get_text_from_url(url) != "")
    #     self.assertEqual(all(bools), True)

    def test_get_text_from_url_regular(self):
        with open(self.mock_data_dir + "regular_url_list", "r") as f:
            urls = f.read().split('\n')
            bools = []
            for url in urls:
                bools.append(pipeline.get_text_from_url(url) != "")
            self.assertEqual(all(bools), True)

    def test_get_wiki_links(self):
        args_permutations = [["title", "author", "publisher", "date", "url", "archive-url"],
                             ["author", "date", "url"],
                             ["date", "url"],
                             ["title"]]
        respective_lengths = [2, 4, 5, 5]
        bools = []
        for i in range(len(args_permutations)):
            args = args_permutations[i]
            length = respective_lengths[i]
            data = pipeline.get_wiki_article_links_info(
                        self.mock_data_dir + "mock_wiki_links",
                        args
                    )
            bools.append(list(data[1].keys()) == args)
            bools.append(len(data[0]) == length)
        self.assertEqual(all(bools), True)

    # def test_find_attr_substr(self):

    # def test_locate_attributes(self):

    # def test_aggregate_data(self):


    def test_word_vectorization(self):
        words = ['hello', 'michaelwan2000']
        words.append(''.join(random.choice('0123456789ABCDEF ') for i in range(500)))
        words.append(''.join(random.choice('0123456789ABCDEF ') for i in range(800)))
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
