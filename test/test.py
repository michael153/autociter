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

import autociter.data.standardize as standardize
import autociter.core.train as train
import autociter.core.pipeline as pipeline

def test_scrape_author_in_article(info, num_points=False):
    """For a list of url, author pairs, find the success rate of scraping the url and
    finding the authors within the text
    """

    if num_points:
        print("Testing {0} datapoints... 'test_scrape_author_in_article'\n\n".format(num_points))
    else:
        print("Testing datapoints... 'test_scrape_author_in_article'\n\n")

    label_lookup = info[1]
    success, total, scrape_failure = 0, 0, 0
    datapoints = info[0][:num_points] if num_points else info[0]

    for t in datapoints:
        url = t[label_lookup['url']]
        authors = t[label_lookup['author']]
        text = standardize.std_text(pipeline.get_text_from_url(url))
        if text == "":
            scrape_failure += 1
            continue
        converted_authors = [standardize.std_word(a, 'author') for a in authors]
        print(str(converted_authors))
        found = all([i in text for i in converted_authors])
        if not found:
            print("\nFailed case: {0}\n".format((url, authors)))
        success += found
        total += 1
    return (success, total, scrape_failure)

resources_path = os.path.dirname(os.path.realpath(__file__)) + '/../resources'
info = pipeline.get_wikipedia_article_links_info(resources_path + '/data.txt', ['url', 'author'])
result = test_scrape_author_in_article(info, 25)

print("{0}/{1} ({3}%) cases passed, {2} scrapes threw errors".format(result[0],
                                                                     result[1],
                                                                     result[2],
                                                                     (100.0*result[0])/result[1]))
