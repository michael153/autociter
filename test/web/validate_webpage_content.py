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
import time

import assets

from autociter.core.pipeline import slice_text
from autociter.data.storage import Table
from autociter.web.webpages import Webpage
from autociter.utils.debugging import debug

import autociter.data.standardization as standardization

SAMPLE_DATA = standardization.standardize(
    Table(assets.MOCK_DATA_PATH + "/citations_sample.csv"), 'table')
IGNORED_FIELDS = {"url", "publisher"}
CONSIDERED_FIELDS = [
    field for field in SAMPLE_DATA.fields if field not in IGNORED_FIELDS
]


def similarity(string1, string2):
    """Return a score representing the similartiy of two strings."""
    return SequenceMatcher(None, string1, string2).ratio()


def contains(string, substring):
    """Return true if string contains a substring similar to substring."""
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
    debug("Starting data preservation test.")
    accuracies = []
    overall = {x: {"found": 0, "total": 0} for x in CONSIDERED_FIELDS}

    no_title_found = []

    for record in sample:
        try:
            if ".pdf" in record["url"]:
                continue
            start_time = time.time()
            defined_values = [(record[field], field)
                              for field in CONSIDERED_FIELDS
                              if (record[field])]
            content = Webpage(record["url"]).content
            standardized_content = slice_text(
                standardization.standardize(content, "text"))
            values_found_in_content = 0
            values_expected_in_content = 0
            for value, field in defined_values:
                location = standardization.find(value, standardized_content,
                                                field)
                if isinstance(location, list):
                    for loc in location:
                        values_expected_in_content += 1
                        overall[field]['total'] += 1
                        if loc != (-1, -1):
                            overall[field]['found'] += 1
                            values_found_in_content += 1
                else:
                    values_expected_in_content += 1
                    overall[field]['total'] += 1
                    if location != (-1, -1):
                        overall[field]['found'] += 1
                        values_found_in_content += 1
                    elif field == 'title':
                        no_title_found.append(record["url"])

            accuracy = values_found_in_content / values_expected_in_content if values_found_in_content else 0
            debug("({0} : {1}) | {2} | {3:.2f}s".format(
                values_found_in_content, values_expected_in_content,
                record["url"],
                time.time() - start_time))
            accuracies.append(accuracy)
        except Exception as ex:  #pylint: disable=broad-except
            debug("Error   | {0} | {1}".format(record["url"], ex))
    average_accuracy = numpy.average(accuracies)
    debug("Data accuracy test complete.\n")
    debug("SUMMARY")
    debug("---")
    debug("Average Accuracy:", average_accuracy)
    debug("# Records Tested:", len(sample))
    debug("")
    for field in overall:
        debug("Field {0}: ({1} / {2} found)".format(
            field, overall[field]['found'], overall[field]['total']))
    debug("\n")
    debug("\n\nUrls w/ no title found: ")
    debug(no_title_found)
    return average_accuracy


def content_start_accuracy(sample):
    """Return average accuracy at determining where content starts.

    This function compares predicted webpage titles, as they are defined by
    Webpage.content, against the actual webpage titles.

    Arguments:
        sample: A Table instance of sample data
    """
    debug("Starting content start test.")

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
            predicted_title = retrieve_title_from_content(
                standardize(webpage.content, "text"), len(expected_title))
            sim = similarity(expected_title.title(), predicted_title.title())
            debug(
                record["url"],
                predicted_title.title(),
                expected_title.title(),
                sim,
                sep="\n")
            debug("\n")
            # If the predicted and actual titles are similar, then the content
            # probably started at the right place.
            if sim > 0.7:
                num_valid += 1
            total += 1
        except Exception as ex:  #pylint: disable=broad-except
            debug("*** Error: {0}\n".format(ex))
    accuracy = num_valid / total

    debug("Content start test complete.\n")
    debug("SUMMARY")
    debug("---")
    debug("accuracy:", accuracy)
    debug("# records tested:", len(sample))
    debug("")

    return accuracy
