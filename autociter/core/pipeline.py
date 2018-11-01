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

import re
import json
import time
import os
import os.path

from autociter.data.storage import Table
from boilerpipe.extract import Extractor
import autociter.data.standardize as standardize
import autociter.data.queries as queries

SUPPORTED_SPECIAL_CHARS = ['-', ':', '.', ' ', '\n', '#']
ENCODING_COL = list(string.ascii_uppercase) + list(string.ascii_lowercase) + \
               list(string.digits) + SUPPORTED_SPECIAL_CHARS
ENCODING_RANGE = len(ENCODING_COL)

# Data Aggregation

def get_text_from_url(url):
    """Preliminary method to extract only the relevant article text from a website
    Alternates:
    https://github.com/goose3/goose3
    https://github.com/misja/python-boilerpipe
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
            reader = PdfFileReader(file)
            num_page = reader.getNumPages()
            contents = reader.getPage(0).extractText()
            if num_page > 1:
                contents += reader.getPage(num_page - 1).extractText()
            scraped_words = re.sub("[^\w]", " ", contents).split()
            return ' '.join(scraped_words)
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(colored("*** Error: Reading pdf in {0} ({1}): {2}".format(func_name, url, e), "red"))
            return ""
    else:
        try:
            text = markdown.get_content(Webpage(url).markdown)
            ### Keeps '#' and '\n'
            # Cleans consecutive newlines into just one (e.g ['\n', '\n', 'a'] --> ['\n', 'a'])
            # Cleans all elements containing '#' into just '#' (e.g. '####' --> '#')
            matched_words = re.findall(r'\S+|\n', re.sub("[^\w#\n]", " ", text))
            words_and_pound_newline = [i for i, j in itertools.zip_longest(matched_words, matched_words[1:]) if i!=j]
            words_and_pound_newline = [('#' if '#' in x else x) for x in words_and_pound_newline]
            words_and_pound_newline = [(x.replace('_', '') if '_' in x else x) for x in words_and_pound_newline]
            ret = ''
            for i in range(len(words_and_pound_newline)-1):
                word = words_and_pound_newline[i]
                if i == 0 or word == '\n' or (i > 0 and words_and_pound_newline[i-1] == '\n'):
                    ret += word
                else:
                    ret += (" " + word)
            print("Text scrape successfully finished in {0} seconds: {1}".format(time.time()-start_time, url))
            return ret

            ### Just characters
            # total_words = re.sub("[^\w]", " ", text).split()
            # return ' '.join(total_words)
        except Exception as e:
            func_name = inspect.getframeinfo(inspect.currentframe()).function
            print(colored("*** Error: Reading text in {0} ({1}): {2}".format(func_name, url, e), "red"))
            return ""

def get_wiki_article_links_info(file, args):
    """Retrieve article information from wikipedia database Tables, and store
    data into a tupled list
    >>> get_wiki_article_links_info('asserts/data.txt', ['url', 'author'])
    """

    print("Reading Wikipedia Article Links from...", file)

    table = standardize.std_table(Table(file)).query(queries.contains(*args))
    data = [tuple([rec[a] for a in args]) for rec in table.records]
    # Return labels in order to remember what each index in a datapoint represents
    labels = {args[x]: x for x in range(len(args))}
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
                matches = search_dates(text, settings={'STRICT_PARSING': True,
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
    std_text = standardize.std_text(text)
    for key, val in citation_dict.items():
        if val:
            data_field = standardize.std_data(val, key)
            if isinstance(data_field, list):
                pos = [find_attr_substr(std_text, d_, key) for d_ in data_field if d_ in std_text]
                if pos:
                    location_dict[key] = pos
            else:
                pos = find_attr_substr(std_text, data_field, key)
                if pos != (-1, -1):
                    location_dict[key] = pos
    return location_dict

def aggregate_data(info, num_points=False):
    """Collect info and manipulate into the proper format to be saved
    as data
    Arguments:
        info, a tuple containing data points, and a label lookup dict
        num_points, the number of datapoints in info to be used
    """

    datapoints, label_lookup = info[0], info[1]
    data = []
    if num_points:
        datapoints = datapoints[:num_points]
    for entry in datapoints:
        url = entry[label_lookup['url']]
        citation_dict = {x: entry[label_lookup[x]] for x in label_lookup.keys()}
        text = slice_text(get_text_from_url(url))
        if text.strip() != "":
            vec = vectorize_text(text)
            if vec:
                entry = {'url': url,
                         'citation_info': {},
                         'article_one_hot': str(hash_vectorization(vec))}
                for key in citation_dict.keys():
                    entry['citation_info'][key] = citation_dict[key]
                entry['locs'] = locate_attributes(text, citation_dict)
                data.append(entry)
    return data

def save_data(file_name, data, override_data=True):
    """Given a file_name and data, a list of tuples containing url link, list of citation info,
    create an entry in the dict in savedArticleData.dat
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
        if override:
            saved_dict = json.load(open(file_name))
        else:
            saved_dict = {}
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

def get_saved_data(file_name):
    """Given a file_name, collect the saved data and return a data dict"""
    if not os.path.isfile(file_name):
        print(colored(">>> Error: Opening file", "red"))
        return {}
    saved_dict = json.load(open(file_name))
    for k in saved_dict.keys():
        str_one_hot = eval(saved_dict[k]['article_one_hot'])
        saved_dict[k]['article_one_hot'] = unhash_vectorization(str_one_hot)
    return saved_dict

# String Vectorization

def clean_to_ascii(c):
    """Converts a non-ASCII character into it's ASCII equivalent

        >>> clean_to_ascii('ç')
        'c'
    """
    special_chars = {
        'a': ['à', 'á', 'â', 'ä', 'æ', 'ã', 'å', 'ā'],
        'c': ['ç', 'ć', 'č'],
        'e': ['è', 'é', 'ê', 'ë', 'ē', 'ė', 'ę'],
        'i': ['î', 'ï', 'í', 'ī', 'į', 'ì'],
        'l': ['ł'],
        'n': ['ñ', 'ń'],
        'o': ['ô', 'ö', 'ò', 'ó', 'œ', 'ø', 'ō', 'õ'],
        's': ['ß', 'ś', 'š'],
        'u': ['û', 'ü', 'ù', 'ú', 'ū'],
        'y': ['ÿ'],
        'z': ['ž', 'ź', 'ż']
    }
    if c in sum(special_chars.values(), []):
        for k in special_chars.keys():
            if c in special_chars[k]:
                return k
    else:
        print("Can't convert: " + str(c))
        return ' '

def one_hot(s):
    """Converts a string s into a one-hot encoded vector with default dimensions
       of 600 by ENCODING_RANGE.
       The column vector will correspond to:
       ['A', 'B', ... 'Z', 'a', 'b', ... 'z', 0, 1, ... 9, '-', ':', '.', ' ', '\n', '#']
       Arguments:
            s: A string s that represents the first and last characters of an article / text
               with dimensions (600, 1)
    """
    mat = [[0 for _ in range(ENCODING_RANGE)] for __ in range(len(s))]
    for i in range(len(s)):
        char = s[i]
        if not ord(char) != 10 and (ord(char) < 127 and ord(char) > 31):
            char = clean_to_ascii(char)
        if char not in ENCODING_COL:
            print(colored("Not in one-hot encoding range: {0}".format(char), 'yellow'))
            char = ' '
        if char.isupper():
            mat[i][ord(char) - 65] = 1
        elif char.islower():
            mat[i][26 + ord(char) - 97] = 1
        elif char.isnumeric():
            mat[i][52 + ord(char) - 48] = 1
        elif char in SUPPORTED_SPECIAL_CHARS:
            ind = len(SUPPORTED_SPECIAL_CHARS) - SUPPORTED_SPECIAL_CHARS.index(char)
            mat[i][ENCODING_RANGE-ind] = 1
    return mat

def slice_text(text, char_len=600):
    """Method that either pads or truncates a text based on the length"""

    def truncate_text(text, text_len=600):
        """Truncates a text so that the return value has a length of text_len by taking the first
        and last characters
        """
        if len(text) > text_len:
            odd = (text_len % 2)
            return text[0:text_len//2] + text[-(text_len + odd)//2:]
        return text

    def pad_text(text, text_len=600):
        """Pads a text with space characters in the middle to preserve the beginning and ending
        while also so that the length of the text is equal to text_len
        """
        if len(text) < text_len:
            cur_len = len(text)
            remainder = text_len - cur_len
            return text[:cur_len//2] + (' ')*remainder + text[cur_len//2:]
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
    RESOURCES_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../resources'
    INFO = get_wiki_article_links_info(RESOURCES_PATH + '/data.txt', ['url', 'author', 'date'])
    NUM_DATA_POINTS = 100
    DATA = aggregate_data(INFO, NUM_DATA_POINTS)
    save_data(RESOURCES_PATH + '/savedArticleData.dat', DATA, override_data=True)

# d = get_saved_data('assets/savedArticleData.dat')
# print(json.dumps(d, sort_keys=True, indent=4))
