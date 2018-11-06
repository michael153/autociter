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
"""Define methods for sampling collections."""
import random


def simple_random_sample(collection, size=30):
    if not hasattr(collection, '__iter__'):
        raise TypeError("collection must be iterable.")
    sample = []
    for _ in range(size):
        random_index = random.randint(0, len(collection) - 1)
        random_element = collection[random_index]
        sample.append(random_element)
    return sample
