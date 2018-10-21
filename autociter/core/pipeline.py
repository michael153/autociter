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
import os.path

from autociter.data.processor import Table
from boilerpipe.extract import Extractor
import autociter.data.standardize as standardize

ENCODING_RANGE = 66

# Data Aggregation

def get_text_from_url(url):
    """Preliminary method to extract only the relevant article text from a website using the
    Python-Boilerpipe API (https://github.com/misja/python-boilerpipe)

    The extractor accurately finds a start of the article, but because it omits divs with short text lengths,
    we must manually get the article (including author) text

    Alternates:
    https://github.com/goose3/goose3

    Misc. References:
    https://stackoverflow.com/questions/4576077/python-split-text-on-sentences

    Failed cases:
    https://www.bbc.com/sport/football/22787925, ['Alasdair Lamont']
    """
    startTime = time.time()
    if ".pdf" in url:
        try:
            r = requests.get(url, stream=True)
            f = io.BytesIO(r.content)
            reader = PdfFileReader(f)
            contents = reader.getPage(pageNumber).extractText()
            extractedWords = re.sub("[^\w]", " ", contents).split()
            return ' '.join(extractedWords)
        except:
            print(">>> Error: Error reading pdf in get_text_from_url")
            return ""
    try:
        cleanedText = Extractor(extractor='CanolaExtractor', url=url).getText()
        allText = Extractor(extractor='KeepEverythingExtractor', url=url).getText()
        # Remove \n and special characters via regex
        extractedWords = re.sub("[^\w]", " ", cleanedText).split()
        totalWords = re.sub("[^\w]", " ", allText).split()
        # Try three (arbitrary amount) of the starting words in extractedWords
        for i in range(3):
            if extractedWords[i] in totalWords:
                totalWords = totalWords[totalWords.index(extractedWords[i]):]
                break
        # Try three (arbitrary amount) of the ending words in extractedWords
        for i in range(1, 4):
            if extractedWords[-i] in totalWords:
                reverseLookupIndex = len(totalWords) - 1 - totalWords[::-1].index(extractedWords[-i])
                totalWords = totalWords[:reverseLookupIndex]
                break
        print("Text scrape successfully finished in {0} seconds".format(time.time() - startTime))
        return ' '.join(totalWords)
    except:
        print(">>> Error: Error reading text in get_text_from_url")
        return ""

def get_wikipedia_article_links_info(file, args):
    """Retrieve article information from wikipedia database Tables, and store
    data into a tupled list

    >>> get_wikipedia_article_links_info('asserts/data.txt', ['url', 'author'])
    """

    def get_attribute(r, arg):
        """Given a row entry in Table r, return the proper value in the table that
        corresponds to the argument arg

        >>> get_attribute(t[0], "url")
        'http://www.iwm.org.uk/memorials/item/memorial/2814'
        """
        if arg in ['title', 'publisher', 'date', 'url', 'archive-url']:
            return r[arg]
        elif arg == 'authors':
            temp_list = [(r["first"], r["last"]), (r["first1"], r["last1"]), (r["first2"], r["last2"])]
            validate_author = lambda x: x[0].strip() not in ["", "null"] and x[1].strip() not in ["", "null"]
            return list(set([' '.join(a) for a in temp_list if validate_author(a)]))

    t = Table(file)
    data = [[] for i in range(len(args))]
    # Prepare urls and authors
    for r in t.records:
        # validate = lambda x: get_attribute(x, 'url') not in ["", [], "null"] #Make sure that url is valid for each table entry
        validate = lambda x: all([get_attribute(x, arg) not in ["", [], "null"] for arg in args]) #Make sure that all datapoints are valid for each table entry
        if validate(r):
            for i in range(len(args)):
                arg = args[i]
                data[i].append(get_attribute(r, arg))
    datapoints = list(zip(*data))
    # Return labels in order to remember what each index in a datapoint represents
    labels = {args[x]: x for x in range(len(args))}
    return (datapoints, labels)

def locate_attributes(text, citation_dict):
    """Return indices of attribute in the text string if it is found"""
    location_dict = {}
    std_text = standardize.std_text(text)
    for k, v in citation_dict.items():
        if type(v) == list:
            for i in v:
                word = standardize.std_word(i, k)
                index = std_text.find(word)
                if index != -1:
                    if k not in location_dict:
                        location_dict[k] = []
                    location_dict[k].append((index, index + len(word)))
        elif v not in ["", "null"]:
            word = standardize.std_word(v, k)
            index = std_text.find(word)
            if index != -1:
                location_dict[k] = (index, index + len(word))
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
        authors = entry[1]
        citation_dict = {x: entry[label_lookup[x]] for x in label_lookup.keys()}
        text = slice_text(get_text_from_url(url))
        if text != "":
            v = vectorize_text(text)
            if v != "":
                d = {'url': url, 'citation_info': {}, 'article_one_hot': str(hash_vectorization(v))}
                for k in citation_dict.keys():
                    d['citation_info'][k] = citation_dict[k]
                d['locs'] = locate_attributes(text, citation_dict)
                data.append(d)
    return data

def save_data(fileName, data):
    """Given a fileName and data, a list of tuples containing url link, list of citation info,
    create an entry in the dict in savedArticleData.dat

    Arguments:
        fileName, a string file name
        data, a list of dicts, each dict contains the citation information, url, and text
              vectorization of an article
    """
    if not os.path.isfile(fileName):
        f = open(fileName, "w+")
        f.write('{}')
        f.close()
    try:
        saved_dict = json.load(open(fileName))
    except:
        saved_dict = {}
    for datapoint in data:
        key = datapoint['url']
        saved_dict[key] = {}
        for keys, val in datapoint['citation_info'].items():
            saved_dict[key][keys] = val
        saved_dict[key]['article_one_hot'] = datapoint['article_one_hot']
        saved_dict[key]['locs'] = datapoint['locs']
    with open(fileName, 'w') as out:
        json.dump(saved_dict, out, sort_keys=True, indent=4)

def get_saved_data(fileName):
    """Given a fileName, collect the saved data and return a data dict"""
    if not os.path.isfile(fileName):
        print(">>> Error: Opening file")
        return {}
    saved_dict = json.load(open(fileName))
    for k in saved_dict.keys():
        saved_dict[k]['article_one_hot'] = unhash_vectorization(eval(saved_dict[k]['article_one_hot']))
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
    """Converts a string s into a one-hot encoded vector with default dimensions of 600 by ENCODING_RANGE.
       The column vector will correspond to ['A', 'B', ... 'Z', 'a', 'b', ... 'z', 0, 1, ... 9, '-', ':', '.', ' ']

       Arguments:
            s: A string s that represents the first and last characters of an article / text
               with dimensions (600, 1)
    """
    encoding_range = ENCODING_RANGE
    mat = [[0 for _ in range(encoding_range)] for __ in range(len(s))]
    for i in range(len(s)):
        char = s[i]
        if not (ord(char) < 127 and ord(char) > 31):
            char = clean_to_ascii(char)
        if char.isupper():
            mat[i][ord(char) - 65] = 1
        elif char.islower():
            mat[i][26 + ord(char) - 97] = 1
        elif char.isnumeric():
            mat[i][52 + ord(char) - 48] = 1
        elif char == '-':
            mat[i][encoding_range-4] = 1
        elif char == ':':
            mat[i][encoding_range-3] = 1
        elif char == '.':
            mat[i][encoding_range-2] = 1
        elif char == ' ':
            mat[i][encoding_range-1] = 1
    return mat

def slice_text(text, char_len=600):
    def truncate_text(text, text_len=600):
        """Truncates a text so that the return value has a length of text_len by taking the first
        and last characters
        """
        if len(text) > text_len:
            odd = (text_len % 2)
            return text[0:text_len//2] + text[-(text_len + odd)//2:]
        else:
            return text
    def pad_text(text, text_len=600):
        """Pads a text with space characters in the middle to preserve the beginning and ending
        while also so that the length of the text is equal to text_len
        """
        if len(text) < text_len:
            cur_len = len(text)
            remainder = text_len - cur_len
            return text[:cur_len//2] + (' ')*remainder + text[cur_len//2:]
        else:
            return text
    if len(text) > char_len:
        text = truncate_text(text, char_len)
    elif len(text) < char_len:
        text = pad_text(text, char_len)
    return text

def vectorize_text(text, char_len=600):
    """Given a string of text (already padded, truncated), convert into one hot matrix"""
    if len(text) != char_len:
        print(">>> Error: Incorrect dimensions of text")
        return []
    return one_hot(text)

def hash_vectorization(vec):
    """Hash a one-hot matrix so that it takes less space, allowing
    data files to be more efficient
    """
    return [v.index(1) for v in vec]

def unhash_vectorization(hashed_vec, encoding_range=ENCODING_RANGE):
    """Unhash hash_vectorization to restore original one-hot matrix"""
    m = [[0 for _ in range(encoding_range)] for __ in range(len(hashed_vec))]
    for i in range(len(hashed_vec)):
        m[i][hashed_vec[i]] = 1
    return m

# Data aggregation
if __name__ == '__main__':
    resources_path = os.path + '/../resources'
    info = get_wikipedia_article_links_info(resources_path + '/data.txt', ['url', 'authors', 'date'])
    data = aggregate_data(info, 50)
    save_data(resources_path + '/savedArticleData.dat', data)

# d = get_saved_data('assets/savedArticleData.dat')
# print(json.dumps(d, sort_keys=True, indent=4))
