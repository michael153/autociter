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
"""Utility script for caching rule data."""
import assets

from autociter.data.storage import Table, Record
from autociter.web.webpages import Webpage

from rnd.creation import analyze
from rnd.evaluation import evaluate

DATA_TABLE = Table(assets.DATA_PATH + "/title_data.csv")


def generate_rules(data_table):
    """Use pattern recoginition algorithm to generate a collection of rules.

    Arguments:
        data_table: A Table instance with fields "url" and "title"

    Returns:
        A collection of Rule instances
    """
    rules = []
    for record in data_table:
        webpage = Webpage(record["url"])
        new_rules = analyze(webpage.source, record["title"])
        rules.extend(new_rules)
    return rules


def evaluate_rules(rules, data_table):
    """Evaluate rules against a data set.

    Arguments:
        rules: A collection of Rule objects
        data_table: A Table instance with fields "url" and "title"

    Returns:
       A collection of Rule instances
    """
    source_to_title = {
        Webpage(record["url"]).source: record["title"] for record in data_table
    }
    return evaluate(rules, source_to_title)


def save_rules(rules, filename="rules.csv"):
    """Save rules to a file so that they can be reconstructed later.

    Arguments:
        rules: A collection of Rule objects
    """
    rule_data = Table(fields=("left", "right", "alpha", "beta"))
    for rule in rules:
        data_entry = Record(
            fields=rule_data.fields,
            values=(rule.left, rule.right, str(rule.alpha), str(rule.beta)))
        rule_data.add(data_entry)
    rule_data.save(filename)


if __name__ == "__main__":
    RULES = generate_rules(DATA_TABLE)
    RULES = evaluate_rules(RULES, DATA_TABLE)
    save_rules(RULES)
