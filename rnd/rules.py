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
import math

from unidecode import unidecode


def standardize(string):
    """Convert string to ASCII."""
    string = unidecode(string)
    string = string.rstrip()
    string = string.lstrip()
    return string


class Rule:

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.alpha = 1
        self.beta = 1

    def __repr__(self):
        return "Rule('{0}', '{1}')".format(self.left, self.right)

    def evaluate(self, string):
        values = set()
        while self.left in string and self.right in string:
            left_start = string.find(self.left)
            left_end = left_start + len(self.left)
            right_start = string.find(self.right, left_end)
            right_end = right_start + len(self.right)
            values.add(string[left_end:right_start])
            string = string[right_end:]
        return values

    def train(self, string, expected):
        if self.evaluate(string):
            self.beta += 1
        if expected in self.evaluate(string):
            self.alpha += 1

    @property
    def magnitude(self):
        return len(self.left) + len(self.right)

    @property
    def weight(self):
        accuracy = self.alpha / self.beta
        dampening = math.log(self.magnitude)
        return dampening * accuracy
