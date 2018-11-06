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
"""Test methods of the Table object defined in data.storage."""
import unittest

from autociter.utils.sampling import simple_random_sample


# pylint: disable=missing-docstring,
class SamplingTest(unittest.TestCase):

    def test_simple_random_sample_returns_correct_sample_size(self):
        collection = list(range(100))
        default_size_sample = simple_random_sample(collection)
        size_five_sample = simple_random_sample(collection, 5)
        self.assertEqual(30, len(default_size_sample))
        self.assertEqual(5, len(size_five_sample))

    def test_simple_random_sample_is_random(self):
        collection = [0, 1]
        large_sample = simple_random_sample(collection, 100000)
        is_even = lambda element: element % 2 == 0
        even_elements = list(filter(is_even, large_sample))
        proportion_even = len(even_elements) / len(large_sample)
        self.assertTrue(0.45 < proportion_even < 0.55)
