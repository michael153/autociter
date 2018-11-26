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


class Rule:

    DAMPENING_CONSTANT = 1.00009210765
    MODIFYING_CONSTANT = 2.73

    def __init__(self, left, right):
        assert left or right
        self.left = left
        self.right = right
        self.alpha = 1
        self.beta = 1

    def __repr__(self):
        return "Rule('{0}', '{1}')".format(self.left, self.right)

    def evaluate(self, string):
        values = set()
        while True:
            offset = 0
            for i in range(len(self.left)):
                left_start = string.find(self.left[i], offset)
                if left_start == -1:
                    return values
                offset = left_start
            
            left_bound = left_start + len(self.left[-1])
            offset = left_bound

            for i in range(len(self.right)):
                right_start = string.find(self.right[i], offset)
                if right_start == -1:
                    return values
                if i == 0:
                    right_bound = right_start
                offset = right_start

            right_end = right_start + len(self.right[-1])
            values.add(string[left_bound:right_bound])
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
        modifier = math.log(self.magnitude, self.MODIFYING_CONSTANT)
        dampening = 1 - pow(self.DAMPENING_CONSTANT, -self.beta)
        return dampening * modifier * accuracy

def get_segments(index,
                 window_left,
                 dir,
                 bounds,
                 min_word_length=5,
                 min_skip_length=2,
                 max_depth=4):

    rules = []
    if index >= bounds[0] and index < bounds[1] and max_depth > 0:
        for rule_length in range(min_word_length, window_left):
            for skip_length in range(min_skip_length,
                                     window_left - rule_length):
                if index + dir * rule_length < bounds[
                        0] or index + dir * rule_length >= bounds[1]:
                    continue

                word_indice = (index, index + dir * rule_length)

                if word_indice[1] < word_indice[0]:
                    word_indice = (word_indice[1], word_indice[0])

                paths = [[word_indice]]

                rest = get_segments(
                    index + dir * (rule_length + skip_length),
                    window_left - rule_length - skip_length, dir, bounds,
                    max_depth - 1)

                if rest:
                    if dir == 1:
                        paths = [paths[0] + r for r in rest]
                    elif dir == -1:
                        paths = [r + paths[0] for r in rest]

                rules += paths
    return rules

def get_left_right_rules_indices(string, substring, bounds, b=18):
    if substring not in string:
        return []
    start = string.find(substring)
    end = start + len(substring)
    rules = []
    for left_segment in get_segments(start, b, -1, bounds):
        for right_segment in get_segments(end, b, 1, bounds):
            rules.append((left_segment, right_segment))
    return rules + get_left_right_rules_indices(string[end:], substring, bounds, b)

def analyze(string, substring, a=1, b=18):
    sequences = get_left_right_rules_indices(string, substring, (0, len(string)), b)
    rules = []
    for seq in sequences:
        left_seq, right_seq = seq[0], seq[1]
        lefts = []
        rights = []
        for indices in left_seq:
            lefts.append(string[indices[0]:indices[1]])
        for indices in right_seq:
            rights.append(string[indices[0]:indices[1]])
        newRule = Rule(lefts, rights)
        rules.append(newRule)
    return rules