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
import time

from autociter.utils.debugging import debug


def evaluate(rules, titles):
    debug("Removing duplicates...")
    # rules = remove_duplicates(rules)
    for i, rule in enumerate(rules):
        debug("Training Rule {0}/{1}: {2} on {3} titles".format(i, len(rules), rule, len(titles)))
        for source_code in titles:
            rule.train(source_code, titles[source_code])
    rules = sorted(rules, key=lambda rule: -rule.weight)

    debug("Rule evaluation complete")
    debug("")
    debug("SUMMARY")
    debug("---")
    for rule in rules[:20]:
	       debug(rule.weight, rule, sep="\t")
    return rules


def remove_duplicates(rules):

    def same(rule1, rule2):
        return rule1.left == rule2.left and rule1.right == rule2.right

    i = 0
    while i < len(rules) - 1:
        to_remove = []
        for j in range(i + 1, len(rules)):
            if same(rules[i], rules[j]):
                to_remove.append(rules[j])
        while to_remove:
            duplicate_rule = to_remove.pop()
            rules.remove(duplicate_rule)
        i += 1
    return rules
