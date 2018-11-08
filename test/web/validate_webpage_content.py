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
import assets

from autociter.data.storage import Table
from autociter.utils.statistics import average
from autociter.web.webpages import Webpage
from autociter.core.pipeline import slice_text

SAMPLE_DATA = Table(assets.MOCK_DATA_PATH + "/citations_sample.csv")
IGNORED_FIELDS = {"url", "date"}
RELEVANT_FIELDS = [
    field for field in SAMPLE_DATA.fields if field not in IGNORED_FIELDS
]
DESIRED_ACCURACY = 0.95


def validate_accuracy_of_webpage_content(sample):
    """Check if webpage content is sufficiently accuracy against a sample.

    Arguments:
        sample: A Table instance of sample data
    """
    average_accuracy = average_accuracy_of_webpage_content(sample)
    if average_accuracy < DESIRED_ACCURACY:
        print("Expected more than {0} accuracy but got {1}.".format(
            DESIRED_ACCURACY, average_accuracy))
    else:
        print(
            "Validation succeeded with {0} accuracy.".format(average_accuracy))


def average_accuracy_of_webpage_content(sample):
    """Return the average correctness of webpage content against a sample.

    Accuracy is defined as the number of values found in the the content
    divided by the number of values expected to be found in the content. We
    expect the webpage content to contain all of the values that are defined in
    the spreadsheet that are also found in the source code.

    Arguments:
        sample: A Table instance of sample data
    """

    def standardize(text):
        return text.lower()

    accuracies = []
    for record in sample:
        webpage = Webpage(record["url"])
        defined_values = {
            record[field] for field in RELEVANT_FIELDS if record[field]
        }
        values_in_source = {
            value for value in defined_values
            if value in standardize(webpage.source)
        }
        expected_values = defined_values.intersection(values_in_source)
        values_in_content = {
            value for value in expected_values
            if value in standardize(slice_text(webpage.content))
        }
        num_values_expected = len(expected_values)
        num_values_found = len(values_in_content)
        differences = expected_values - values_in_content
        if differences:
            print("[{0}, {1}] {2}".format(num_values_found, num_values_expected,
                                          record["url"]))
            print("Diff: {0}".format(differences))
        else:
            print("ok...{0}".format(record["url"]))
        accuracy = num_values_found / num_values_expected
        accuracies.append(accuracy)
    return average(accuracies)


if __name__ == "__main__":
    validate_accuracy_of_webpage_content(SAMPLE_DATA)
