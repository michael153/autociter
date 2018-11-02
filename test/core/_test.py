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
import datetime
import inspect

from termcolor import colored
from dateparser.search import search_dates

import autociter.data.standardization as standardization
import autociter.core.pipeline as pipeline


def find_attr_substr(text, word, category):
    """Given a string word and the type of data it is (i.e 'date'),
        return the beginning and ending index of the substring within
        text if found, otherwise (-1, -1)
        """
    if category == 'date':
        try:
            reference_date = datetime.datetime.strptime(word, '%m/%d/%y')
            # Pass an impossible relative base so that relative words like "today" won't be detected
            matches = search_dates(
                text,
                settings={
                    'STRICT_PARSING': True,
                    'RELATIVE_BASE': datetime.datetime(1000, 1, 1, 0, 0)
                })
            if matches:
                for original_text, match in matches:
                    if reference_date.date() == match.date():
                        index = text.find(original_text)
                        return (index, index + len(original_text))
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(colored(">>> Error in {0}: {1}".format(func_name, e), "red"))
            return (-1, -1)
    else:
        index = text.find(word)
        if index != -1:
            return (index, index + len(word))
    return (-1, -1)


def find_attr_in_scraped_article(info, attributes, num_points=False):
    """For a list of url, author pairs, find the success rate of scraping the url and
    finding the authors within the text
    """

    if num_points:
        print("Testing {0} datapoints... 'find_attr_in_scraped_article'\n\n".
              format(num_points))
    else:
        print("Testing datapoints... 'find_attr_in_scraped_article'\n\n")

    datapoints = info[0][:num_points] if num_points else info[0]
    total, scrape_failure = 0, 0
    failed_urls = []

    for entry in datapoints:
        url = entry[info[1]['url']]
        data_fields = [entry[info[1][attr]] for attr in attributes]
        text = standardization.std_text(pipeline.get_text_from_url(url))
        if text == "":
            scrape_failure += 1
            continue

        std_fields = [(standardization.std_data(f, a), a)
                      for f, a in zip(data_fields, attributes)]
        pass_case = True

        for field, attribute in std_fields:
            if isinstance(field, list):
                for i in field:
                    pass_case = pass_case and (find_attr_substr(
                        text, i, attribute) != (-1, -1))
                    if not pass_case:
                        break
            else:
                pass_case = pass_case and (find_attr_substr(
                    text, field, attribute) != (-1, -1))
            if not pass_case:
                break

        if not pass_case:
            print(
                colored(
                    "*** Error: Failed case: {0}".format((url, data_fields)),
                    'cyan', 'on_red'))
            failed_urls.append(url)

        total += 1
    return (total - len(failed_urls), total, scrape_failure, failed_urls)


ASSETS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../assets'
INFO = pipeline.get_wiki_article_links_info(ASSETS_PATH + '/data/citations.csv',
                                            ['url', 'author'])
NUM_DATA_POINTS = 20
RES = find_attr_in_scraped_article(INFO, ['author'], NUM_DATA_POINTS)

print("{0}/{1} ({3}%) cases passed, {2} scrapes threw errors".format(
    RES[0], RES[1], RES[2], (100.0 * RES[0]) / RES[1]))

print(colored("\n\nFailed Urls:\n{0}".format('\n'.join(RES[3])), "red"))
