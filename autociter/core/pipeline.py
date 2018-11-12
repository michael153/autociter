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
import itertools
import requests

from PyPDF2 import PdfFileReader
from termcolor import colored
from dateparser.search import search_dates

import autociter.data.standardization as standardization
import autociter.data.queries as queries
from autociter.utils.decorators import timeout
from autociter.data.storage import Table
from autociter.web.webpages import Webpage

ASSETS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../assets'
WIKI_FILE_PATH = ASSETS_PATH + '/data/citations.csv'
BAD_WIKI_LINKS_PATH = ASSETS_PATH + '/data/bad_links.dat'
ARTICLE_DATA_FILE_PATH = ASSETS_PATH + '/data/article_data.dat'

SUPPORTED_SPECIAL_CHARS = ['-', ':', '.', ' ', '\n', '#']
ENCODING_COL = list(string.ascii_uppercase) + list(string.ascii_lowercase) + \
               list(string.digits) + SUPPORTED_SPECIAL_CHARS
ENCODING_RANGE = len(ENCODING_COL)

# Data Aggregation


def clean_text(text):
    """Method that cleans a string to only include relevant characters and words"""
    text = text.replace('\'', '')
    text = text.replace('\"', '')
    matched_words = re.findall(r'\S+|\n', re.sub("[^\w#\n]", " ", text))
    words_and_pound_newline = [
        i for i, j in itertools.zip_longest(matched_words, matched_words[1:])
        if i != j
    ]
    words_and_pound_newline = [('#' if '#' in x else x)
                               for x in words_and_pound_newline]
    words_and_pound_newline = [(x.replace('_', '') if '_' in x else x)
                               for x in words_and_pound_newline]
    ret = ''
    for i in range(len(words_and_pound_newline)):
        word = words_and_pound_newline[i]
        if i == 0 or word == '\n' or (i > 0 and
                                      words_and_pound_newline[i - 1] == '\n'):
            ret += word
        else:
            ret += (" " + word)
    return ret

@timeout(15)
def get_text_from_url(url, verbose=False):
    """Preliminary method to extract only the relevant article text from a website
    Failed cases:
    - https://www.bbc.com/sport/football/22787925, ['Alasdair Lamont']
    - http://ws680.nist.gov/publication/get_pdf.cfm?pub_id=101240', ['William Grosshandler']
    - https://nypost.com/2011/09/19/7-world-trade-center-fully-leased/ (Still gives
      boilerplate info such as 'View author archive', 'email the author', 'etc')
    - https://www.nytimes.com/2001/12/20/nyregion/nation-challenged-trade-center-city-had-been-warned-fuel-tank-7-world-trade.html
      (Gives unnecessary '\n' in title)
    - https://www.politico.eu/article/monster-at-the-berlaymont-martin-selmayr-european-commission-jean-claude-juncker/
      (HTTP Error 403: Forbidden)
    """
    start_time = time.time()
    if ".pdf" in url:
        try:
            req = requests.get(url, stream=True)
            file = io.BytesIO(req.content)
            reader = PdfFileReader(file, strict=False)
            num_page = reader.getNumPages()
            contents = reader.getPage(0).extractText()
            if num_page > 1:
                contents += reader.getPage(num_page - 1).extractText()
            return clean_text(contents)
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(
                colored(
                    "*** Error: Reading pdf in {0} ({1}): {2}".format(
                        func_name, url, e), "red"))
            return ""
    else:
        try:
            text = clean_text(Webpage(url).content)
            if verbose:
                print("Text scrape successfully finished in {0} seconds: {1}".
                      format(time.time() - start_time, url))
            return text
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(
                colored(
                    "*** Error: Reading text in {0} ({1}): {2}".format(
                        func_name, url, e), "red"))
            return ""


def get_wiki_article_links_info(file,
                                args,
                                num=1000,
                                already_collected=[],
                                verbose=False):
    """Retrieve article information from wikipedia database Tables, and store
    data into a tupled list
    >>> get_wiki_article_links_info('asserts/data.txt', ['url', 'author'])
    """
    if verbose:
        print("Reading Wikipedia Article Links from...", file)
    start_time = time.time()
    table = standardization.std_table(Table(file)).query(
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
    if verbose:
        print("Links successfully collected in {0} seconds\n".format(
            time.time() - start_time))
    return (data, labels)


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


def locate_attributes(text, citation_dict):
    """Return indices of attribute in the text string if it is found"""

    location_dict = {}
    std_text = standardization.std_text(text)
    for key, val in citation_dict.items():
        if val:
            data_field = standardization.std_data(val, key)
            if isinstance(data_field, list):
                pos = [
                    find_attr_substr(std_text, d_, key) for d_ in data_field
                    if d_ in std_text
                ]
                if pos:
                    location_dict[key] = pos
            else:
                pos = find_attr_substr(std_text, data_field, key)
                if pos != (-1, -1):
                    location_dict[key] = pos
    return location_dict


def aggregate_data(info, verbose=False):
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
    if verbose:
        print("Getting {0} points...".format(len(datapoints)))
    for entry in datapoints:
        url = entry[label_lookup['url']]
        citation_dict = {
            x: entry[label_lookup[x]]
            for x in label_lookup.keys()
        }
        try:
            text = slice_text(get_text_from_url(url, verbose))
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
        WIKI_FILE_PATH, ['url', 'author', 'date'],
        num=NUM_DATA_POINTS,
        already_collected=ALREADY_COLLECTED_KEYS,
        verbose=True)

    DATA = aggregate_data(INFO, verbose=True)
    save_data(ARTICLE_DATA_FILE_PATH, DATA, override_data=OVERRIDE_DATA)

# d = get_saved_data('assets/article_data.dat')
# print(json.dumps(d, sort_keys=True, indent=4))
