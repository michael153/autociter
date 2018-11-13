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
"""Test functions, methods, and objects defined in rnd.rules."""
import unittest
import math

from rnd.rules import Rule, standardize


# pylint: disable=missing-docstring
class RulesTest(unittest.TestCase):

    def test_standardize(self):
        self.assertEqual("Bei Jing", standardize("北京"))
        self.assertEqual("Skoda", standardize("Škoda"))

    def test_evaluate(self):
        rule = Rule("03", "16")
        values = rule.evaluate("03foo16bar03baz16")
        self.assertEqual({"foo", "baz"}, values)

    def test_train(self):
        rule = Rule("03", "16")
        self.assertTrue(rule.alpha == 1 and rule.beta == 1)
        rule.train("03foo16", "bar")
        self.assertTrue(rule.alpha == 1 and rule.beta == 2)
        rule.train("17foo26", "baz")
        self.assertTrue(rule.alpha == 1 and rule.beta == 2)
        rule.train("03foo16", "foo")
        self.assertTrue(rule.alpha == 2 and rule.beta == 3)

    def test_magnitude(self):
        rule = Rule("03", "16")
        self.assertEqual(4, rule.magnitude)

    def test_weight(self):
        rule = Rule("03", "16")
        self.assertEqual(math.log(4) * 1, rule.weight)
        rule.train("03foo16", "bar")
        self.assertEqual(math.log(4) * 0.5, rule.weight)
