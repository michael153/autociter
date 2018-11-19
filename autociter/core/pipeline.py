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
"""Data pipeline file that extracts and prepares data for analysis"""

import datetime
import inspect
import io
import json
import os
import os.path
import re
import string
import sys
import time
import requests

from PyPDF2 import PdfFileReader
from termcolor import colored

from dateparser.search import search_dates

import autociter.data.standardization as standardization
import autociter.data.queries as queries
from autociter.data.storage import Table
from autociter.web.webpages import Webpage
from autociter.utils.decorators import timeout
from autociter.utils.debugging import debug

ASSETS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../assets'
WIKI_FILE_PATH = ASSETS_PATH + '/data/citations.csv'
BAD_WIKI_LINKS_PATH = ASSETS_PATH + '/data/bad_links.dat'
ARTICLE_DATA_FILE_PATH = ASSETS_PATH + '/data/article_data.dat'

SUPPORTED_SPECIAL_CHARS = ['-', ':', '.', ' ', '\n', '#']
ENCODING_COL = list(string.ascii_uppercase) + list(string.ascii_lowercase) + \
               list(string.digits) + SUPPORTED_SPECIAL_CHARS
ENCODING_RANGE = len(ENCODING_COL)

# Data Aggregation


@timeout(15)
def get_text_from_pdf(pdf_url):
    """Method to retrieve text from an online pdf"""
    start_time = time.time()
    try:
        req = requests.get(pdf_url, stream=True)
        file = io.BytesIO(req.content)
        reader = PdfFileReader(file, strict=False)
        num_pages = reader.getNumPages()
        contents = reader.getPage(0).extractText()
        if num_pages > 1:
            contents += reader.getPage(num_pages - 1).extractText()
        debug("PDF scrape successfully finished in {0} seconds: {1}".format(
            time.time() - start_time, pdf_url))
        return standardization.standardize(contents, "text")
    except Exception as error:
        func_name = inspect.getframeinfo(inspect.currentframe()).function
        debug(
            colored(
                "*** Error: Reading pdf in {0} ({1}): {2}".format(
                    func_name, pdf_url, error), "red"))
        return ""


@timeout(15)
def get_text_from_url(url):
    """Method to get text from any url"""
    start_time = time.time()
    if ".pdf" in url:
        return get_text_from_pdf(url)
    else:
        try:
            text = standardization.standardize(Webpage(url).content, "text")
            debug(
                "Text scrape successfully finished in {0} seconds: {1}".format(
                    time.time() - start_time, url))
            return text
        except Exception as error:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            debug(
                colored(
                    "*** Error: Reading text in {0} ({1}): {2}".format(
                        func_name, url, error), "red"))
            return ""


@timeout(15)
def get_content_from_url(url):
    # Extracts only the ceontent / specific text from a da
    try:
        return slice_text(get_text_from_url(url))
    except Exception as error:
        return ""


def get_wiki_article_links_info(file, args, num=1000, already_collected=[]):
    """Retrieve article information from wikipedia database Tables, and store
    data into a tupled list
    >>> get_wiki_article_links_info('asserts/data.txt', ['url', 'author'])
    """
    debug("Reading Wikipedia Article Links from...", file)
    start_time = time.time()
    table = standardization.standardize(Table(file), 'Table').query(
        queries.contains(*args))
    data = []
    total = 0
    for rec in table.records:
        url = rec['url']
        if url not in already_collected:
            data.append(tuple([rec[a] for a in args]))
            total += 1
        if total == num:
            break

    # data = [tuple([rec[a] for a in args]) for rec in table.records]
    # Return labels in order to remember what each index in a datapoint represents
    labels = {args[x]: x for x in range(len(args))}
    debug("Links successfully collected in {0} seconds\n".format(time.time() -
                                                                 start_time))
    return (data, labels)


def locate_attributes(text, citation_dict):
    """Return indices of attribute in the text string if it is found"""
    location_dict = {}
    std_text = standardization.standardize(text, 'text')
    for key, val in citation_dict.items():
        if key != 'url' and val:
            data_field = standardization.standardize(val, key)
            pos = standardization.find(data_field, std_text, key)
            if pos and (isinstance(data_field, list) or pos != (-1, -1)):
                location_dict[key] = pos
    return location_dict


def aggregate_data(info):
    """Collect info and manipulate into the proper format to be saved
    as data
    Arguments:
        info, a tuple containing data points, and a label lookup dict
    """

    datapoints, label_lookup = info[0], info[1]
    data = []
    try:
        bad_links = json.load(open(BAD_WIKI_LINKS_PATH))
    except:
        bad_links = {}
    debug("Getting {0} points...".format(len(datapoints)))
    for entry in datapoints:
        url = entry[label_lookup['url']]
        citation_dict = {
            x: entry[label_lookup[x]]
            for x in label_lookup.keys()
        }
        try:
            text = get_content_from_url(url)
            if text.strip() != "":
                vec = vectorize_text(text)
                if vec:
                    entry = {
                        'url': url,
                        'citation_info': {},
                        'article_one_hot': str(hash_vectorization(vec))
                    }
                    for key in citation_dict.keys():
                        entry['citation_info'][key] = citation_dict[key]
                    entry['locs'] = locate_attributes(text, citation_dict)
                    data.append(entry)
            else:
                bad_links[url] = time.time()
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(colored(">>> Error in {0}: {1}".format(func_name, e), "red"))
    with open(BAD_WIKI_LINKS_PATH, 'w') as out:
        json.dump(bad_links, out, sort_keys=True, indent=4)
    return data


def save_data(file_name, data, override_data=True):
    """Given a file_name and data, a list of tuples containing url link, list of citation info,
    create an entry in the dict in article_data.dat
    Arguments:
        file_name, a string file name
        data, a list of dicts, each dict contains the citation information, url, and text
              vectorization of an article
    """
    aggregate_keys = ('article_one_hot', 'locs')

    if not os.path.isfile(file_name):
        file = open(file_name, "w+")
        file.write('{}')
        file.close()

    try:
        if override_data:
            saved_dict = {}
        else:
            saved_dict = json.load(open(file_name))
    except:
        saved_dict = {}

    for datapoint in data:
        chosen_key = datapoint['url']
        saved_dict[chosen_key] = {}
        for key, val in datapoint['citation_info'].items():
            saved_dict[chosen_key][key] = val
        for key in aggregate_keys:
            saved_dict[chosen_key][key] = datapoint[key]
    with open(file_name, 'w') as out:
        json.dump(saved_dict, out, sort_keys=True, indent=4)


def get_saved_keys(file_name):
    """Given a file_name, collect the saved data and return a data dict"""
    if not os.path.isfile(file_name):
        print(colored(">>> Error: Opening file {0}".format(file_name), "red"))
        return []
    saved_dict = json.load(open(file_name))
    return list(saved_dict.keys())


def get_saved_data(file_name):
    """Given a file_name, collect the saved data and return a data dict"""
    if not os.path.isfile(file_name):
        print(colored(">>> Error: Opening file {0}".format(file_name), "red"))
        return {}
    saved_dict = json.load(open(file_name))
    for k in saved_dict.keys():
        str_one_hot = eval(saved_dict[k]['article_one_hot'])
        saved_dict[k]['article_one_hot'] = unhash_vectorization(str_one_hot)
    return saved_dict


# String Vectorization


def one_hot(str_):
    """Converts a string s into a one-hot encoded vector with default dimensions
       of 600 by ENCODING_RANGE.
       The column vector will correspond to:
       ['A', 'B', ... 'Z', 'a', 'b', ... 'z', 0, 1, ... 9, '-', ':', '.', ' ', '\n', '#']
       Arguments:
            s: A string s that represents the first and last characters of an article / text
               with dimensions (600, 1)
    """
    mat = [[0 for _ in range(ENCODING_RANGE)] for __ in range(len(str_))]
    for i in range(len(str_)):
        char = str_[i]
        if ord(char) != 10 and not (ord(char) < 127 and ord(char) > 31):
            char = standardization.clean_to_ascii(char)
        if char not in ENCODING_COL:
            print(
                colored("Not in one-hot encoding range: {0}".format(char),
                        'yellow'))
            char = ' '
        if char.isupper():
            mat[i][ord(char) - 65] = 1
        elif char.islower():
            mat[i][26 + ord(char) - 97] = 1
        elif char.isnumeric():
            mat[i][52 + ord(char) - 48] = 1
        elif char in SUPPORTED_SPECIAL_CHARS:
            ind = len(SUPPORTED_SPECIAL_CHARS) - SUPPORTED_SPECIAL_CHARS.index(
                char)
            mat[i][ENCODING_RANGE - ind] = 1
    return mat


def slice_text(text, char_len=600):
    """Method that either pads or truncates a text based on the length"""

    def truncate_text(text, text_len=600):
        """Truncates a text so that the return value has a length of text_len by taking the first
        and last characters
        """
        if len(text) > text_len:
            odd = (text_len % 2)
            return text[0:text_len // 2] + text[-(text_len + odd) // 2:]
        return text

    def pad_text(text, text_len=600):
        """Pads a text with space characters in the middle to preserve the beginning and ending
        while also so that the length of the text is equal to text_len
        """
        if len(text) < text_len:
            cur_len = len(text)
            remainder = text_len - cur_len
            return text[:cur_len // 2] + (' ') * remainder + text[cur_len //
                                                                  2:]
        return text

    if len(text) > char_len:
        text = truncate_text(text, char_len)
    elif len(text) < char_len:
        text = pad_text(text, char_len)
    return text


def unvectorize_text(vec):
    ret = ''
    for row in vec:
        ret += ENCODING_COL[row.index(1)]
    return ret


def vectorize_text(text, char_len=600):
    """Given a string of text (already padded, truncated), convert into one hot matrix"""
    if len(text) != char_len:
        print(colored(">>> Error: Incorrect dimensions of text", "red"))
        return []
    return one_hot(text)


def hash_vectorization(vec):
    """Hash a one-hot matrix so that it takes less space, allowing
    data files to be more efficient
    """
    return [v.index(1) for v in vec]


def unhash_vectorization(hashed_vec, encoding_range=ENCODING_RANGE):
    """Unhash hash_vectorization to restore original one-hot matrix"""
    mat = [[0 for _ in range(encoding_range)] for __ in range(len(hashed_vec))]
    for i in range(len(hashed_vec)):
        mat[i][hashed_vec[i]] = 1
    return mat


# Data aggregation
if __name__ == '__main__':
    print(colored("Reading in arguments: {0}".format(sys.argv), "yellow"))
    OVERRIDE_DATA = True
    NUM_DATA_POINTS = 1000
    ALREADY_COLLECTED_KEYS = []

    if len(sys.argv) > 1:
        NUM_DATA_POINTS = int(sys.argv[1])
        if "-append" in sys.argv:
            OVERRIDE_DATA = False
            ALREADY_COLLECTED_KEYS = get_saved_keys(
                ARTICLE_DATA_FILE_PATH) + get_saved_keys(BAD_WIKI_LINKS_PATH)
            print(
                colored(
                    "{0} links already scraped...".format(
                        len(ALREADY_COLLECTED_KEYS)), "yellow"))

    print("\n")
    INFO = get_wiki_article_links_info(
        WIKI_FILE_PATH, ['url', 'title', 'author', 'date'],
        num=NUM_DATA_POINTS,
        already_collected=ALREADY_COLLECTED_KEYS)

    DATA = aggregate_data(INFO)
    save_data(ARTICLE_DATA_FILE_PATH, DATA, override_data=OVERRIDE_DATA)

# d = get_saved_data('assets/article_data.dat')
# print(json.dumps(d, sort_keys=True, indent=4))
