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
"""Define functions for statistical analysis."""


IDENTITY = lambda element: element


def average(collection, function=IDENTITY):
    """Compute the arithmatic average of some collection.

    Arguments:
        collection: A collection
        function: A single-argument function that maps each element of the
                  collection to a value of a type that supports addition.
    """
    total = 0
    for element in collection:
        total += function(element)
    return total / len(collection)
