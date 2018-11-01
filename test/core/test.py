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
# Author: Michael Wan <m.wan@berkeley.edu>
"""Test various functions and their practicality / success rate"""
import os

from termcolor import colored

import autociter.data.standardize as standardize
import autociter.core.pipeline as pipeline


def find_attr_in_text(article_text, single_field):
    """For a text (representing the article), check whether the string
    single_field can be located within the text
    """
    return single_field in article_text

def find_attr_in_scraped_article(info, attributes, num_points=False):
    """For a list of url, author pairs, find the success rate of scraping the url and
    finding the authors within the text
    """

    if num_points:
        print("Testing {0} datapoints... 'find_attr_in_scraped_article'\n\n".format(num_points))
    else:
        print("Testing datapoints... 'find_attr_in_scraped_article'\n\n")

    datapoints = info[0][:num_points] if num_points else info[0]
    success, total, scrape_failure = 0, 0, 0
    failed_urls = []

    for entry in datapoints:
        url = entry[info[1]['url']]
        data_fields = [entry[info[1][attr]] for attr in attributes]
        text = standardize.std_text(pipeline.get_text_from_url(url))
        if text == "":
            scrape_failure += 1
            continue

        std_fields = [standardize.std_data(f, a) for f, a in zip(data_fields, attributes)]
        pass_case = True

        for field in std_fields:
            if isinstance(field, list):
                for i in field:
                    pass_case = pass_case and find_attr_in_text(text, i)
            else:
                pass_case = pass_case and find_attr_in_text(text, field)
            if not pass_case:
                break

        if not pass_case:
            print(colored("*** Error: Failed case: {0}".format((url, data_fields)), 'cyan', 'on_red'))
            failed_urls.append(url)

        success += pass_case
        total += 1
    return (success, total, scrape_failure, failed_urls)

RESOURCES_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../resources'
INFO = pipeline.get_wiki_article_links_info(RESOURCES_PATH + '/data.txt', ['url', 'author'])
NUM_DATA_POINTS = 20
RES = find_attr_in_scraped_article(INFO, ['author'], NUM_DATA_POINTS)

print("{0}/{1} ({3}%) cases passed, {2} scrapes threw errors".format(RES[0],
                                                                     RES[1],
                                                                     RES[2],
                                                                     (100.0*RES[0])/RES[1]))

print(colored("\n\nFailed Urls:\n{0}".format('\n'.join(RES[3])), "red"))
