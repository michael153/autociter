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
"""Define functions for verifying the accuracy of content extractors."""
from difflib import SequenceMatcher

import numpy

import assets
import autociter.core.pipeline as pipeline

from autociter.data.storage import Table
from autociter.web.webpages import Webpage
from autociter.core.pipeline import slice_text

SAMPLE_DATA = Table(assets.MOCK_DATA_PATH + "/citations_sample.csv")
IGNORED_FIELDS = {"url", "date"}
CONSIDERED_FIELDS = [
    field for field in SAMPLE_DATA.fields if field not in IGNORED_FIELDS
]


def similarity(string1, string2):
    """Return a score representing the similartiy of two strings."""
    return SequenceMatcher(None, string1, string2).ratio()


def contains(string, substring):
    for index in range(len(string)):
        current = string[index:index + len(substring)]
        if similarity(current, substring) > 0.7:
            return True
    return False


def data_preservation_accuracy(sample):
    """Return the average correctness of webpage content against a sample.

    Accuracy is defined as the number of values found in the the content
    divided by the number of values expected to be found in the content. We
    expect the webpage content to contain all of the values that are defined in
    the spreadsheet that are also found in the source code.

    Arguments:
        sample: A Table instance of sample data
    """
    accuracies = []
    for record in sample:
        try:
            webpage = Webpage(record["url"])
            defined_values = {
                record[field] for field in CONSIDERED_FIELDS if record[field]
            }
            values_in_source = {
                value for value in defined_values
                if contains(webpage.source, value)
            }
            # expected_values = defined_values.intersection(values_in_source)
            expected_values = defined_values
            values_in_content = {
                value for value in expected_values
                if contains(webpage.content, value)
            }
            num_values_expected = len(expected_values)
            num_values_found = len(values_in_content)
            accuracy = num_values_expected / num_values_found if num_values_found else 0
            print("{0}: {1}/{2} values found".format(record["url"], num_values_found, num_values_expected))
            accuracies.append(accuracy)
        except Exception as e:
            print("*** Error for url {0}: {1}".format(record["url"], e))
    return numpy.average(accuracies)


def content_start_accuracy(sample):
    """Return average accuracy at determining where content starts.

    This function compares predicted webpage titles, as they are defined by
    Webpage.content, against the actual webpage titles.

    Arguments:
        sample: A Table instance of sample data
    """

    def retrieve_title_from_content(content, len_title):
        whitespace_index = content.find(" ")
        title = content[whitespace_index + 1:whitespace_index + 1 + len_title]
        return title.rstrip().lstrip()

    num_valid = 0
    total = 0
    for record in sample:
        webpage = Webpage(record["url"])
        expected_title = record["title"]
        try:
            predicted_title = retrieve_title_from_content(standardization.standardize(webpage.content, "text"),
                                                          len(expected_title))
            sim = similarity(expected_title.title(), predicted_title.title())
            print(record["url"], predicted_title.title(), expected_title.title(), sim, sep="\n")
            print("\n")
            # If the predicted and actual titles are similar, then the content
            # probably started at the right place.
            if sim > 0.7:
                num_valid += 1
            total += 1
        except Exception as e:
            print("*** Error: {0}\n".format(str(e)))
    return (num_valid / total)
