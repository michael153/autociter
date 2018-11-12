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

import assets

from autociter.data.storage import Table
from autociter.data.standardization import std_text
from autociter.utils.statistics import average
from autociter.web.webpages import Webpage
from autociter.core.pipeline import slice_text

SAMPLE_DATA = Table(assets.MOCK_DATA_PATH + "/citations_sample.csv")
IGNORED_FIELDS = {"url", "date"}
CONSIDERED_FIELDS = [
    field for field in SAMPLE_DATA.fields if field not in IGNORED_FIELDS
]


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
        webpage = Webpage(record["url"])
        defined_values = {
            record[field] for field in CONSIDERED_FIELDS if record[field]
        }
        values_in_source = {
            value for value in defined_values
            if value in std_text(webpage.source)
        }
        expected_values = defined_values.intersection(values_in_source)
        values_in_content = {
            value for value in expected_values
            if value in std_text(slice_text(webpage.content))
        }
        num_values_expected = len(expected_values)
        num_values_found = len(values_in_content)
        accuracies.append(num_values_found / num_values_expected)
    return average(accuracies)


def title_recognition_accuracy(sample):
    """Return average accuracy at identifying webpage titles.

    This function compares predicted webpage titles, as they are defined by
    Webpage.content, against the actual webpage titles.

    Arguments:
        sample: A Table instance of sample data
    """

    def similarity(string1, string2):
        """Return a score representing the similartiy of two strings."""
        return SequenceMatcher(None, string1, string2).ratio()

    def retrieve_title_from_content(content):
        """Retrieve the predicted title from a webpage's content.

        This function assumes that the title is in a heading at the top of
        content, and that content is formatted in markdown.

        Arguments:
            content: A string returned by a webpage's content property

        >>> retrieve_title_from_content("# Foo Bar \nBaz")
        'Foo Bar'
        """
        whitespace_index = content.find(" ")
        newline_index = content.find("\n", whitespace_index)
        return content[whitespace_index + 1:newline_index].rstrip()

    accuracies = []
    for record in sample:
        webpage = Webpage(record["url"])
        expected_title = record["title"]
        predicted_title = retrieve_title_from_content(webpage.content)
        print(similarity(expected_title, predicted_title), "\n", expected_title, "\n", predicted_title)
        accuracies.append(similarity(expected_title, predicted_title))
    return average(accuracies)
