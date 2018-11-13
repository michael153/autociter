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
"""Library that provides method to standardize certain words so they can properly
located within a text"""

import re
import itertools
import datetime

from dateparser.search import search_dates

from autociter.data.storage import Table, Record
from autociter.data.queries import contains


def standardize(data, datatype):
    """Define methods that standardize fields into a singular format that is logical
    and searchable
    """

    def std_table(table):
        """Standardizes a default Table object so that it can be processed by
        pipeline. (i.e Author field is created from first, last, first1, last1, etc.)
        """
        std_fields = [
            "title", "author", "publisher", "date", "url", "archive-url"
        ]
        ret = Table(fields=std_fields)
        for rec in table.records:
            author_fields = [("first", "last"), ("first1", "last1"),
                             ("first2", "last2")]
            authors = []
            for i in author_fields:
                author = (rec[i[0]] + " " + rec[i[1]]).strip()
                if author != "":
                    authors.append(author)
            values = []
            for attr in std_fields:
                if contains(attr)(rec):
                    values.append(rec[attr])
                elif attr == 'author':
                    values.append(list(set(authors)))
                else:
                    values.append("")
            ret.add(Record(std_fields, values))
        return ret

    def std_text(text):
        """Standardizes a string representing article text
        Resources: https://stackoverflow.com/questions/19785458/capitalization-of-sentences-in-python
        """

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

        def uppercase(matchobj):
            return matchobj.group(0).upper()

        def capitalize(s):
            return re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)',
                          uppercase, s)

        text = clean_text(text)
        return capitalize(text)

    def std_author(authors):
        """Method for standardizing a field if it is a list of authors"""
        return [
            ' '.join([name.capitalize() for name in author.replace('.', '').replace('-', ' ').split(' ')])
            for author in authors
        ]

    def std_date(date):
        """Method for standardizing a field if it is a date"""
        base = datetime.datetime(1000, 1, 1, 0, 0)
        matches = search_dates(
            date,
            settings={
                'STRICT_PARSING': True,
                'RELATIVE_BASE': base
            })
        if matches and matches[0][1] - base > datetime.timedelta(days=2 * 365):
            return matches[0][1].strftime('%m/%d/%y')
        return date.lower().replace(',', ' ').replace('-', ' ')

    def std_title(title):
        """Method for standardizing a field if it is a title"""
        return title.title()

    def std_url(url):
        """Method to standardize a url"""
        return url

    try:
        if datatype.lower() in ["table", "text", "author", "date", "title", "url"]:
            return eval("std_{0}(data)".format(datatype.lower()))
        else:
            print(
                "*** Error in standardization.standardize: {0} not standardizable"
                .format(datatype))
            return data
    except Exception as e:
        print("*** Error in standardization.standardize: {0}".format(e))
        return ""


def find(field, text, datatype):
    """Attempts to locate a field as a substring of text based on its datatype.
    Assumes text is cleaned by pipeline's clean_text"""

    def find_generic(field, text):
        """Basic method for finding any generic field within a text"""
        index = text.find(field)
        if index != -1:
            return (index, index + len(field))
        return (-1, -1)

    def find_singular_author(author, text):
        """Helper method for finding a singular author"""
        return find_generic(author.lower(), text.lower())

    def find_author(authors, text):
        """Method for finding an "author" field (a list of authors) in a text"""
        authors = standardize(authors, 'author')
        ret = []
        for author in authors:
            pos = find_singular_author(author, text)
            if pos != (-1, -1):
                ret.append(pos)
        return ret

    def find_date(date, text):
        """Method for finding a date field in a text"""
        date = datetime.datetime.strptime(date, '%m/%d/%y')
        # Pass an impossible relative base so that relative words like "today" won't be detected
        matches = search_dates(
            text,
            settings={
                'STRICT_PARSING': True,
                'RELATIVE_BASE': datetime.datetime(1000, 1, 1, 0, 0)
            })
        if matches:
            for original_text, match in matches:
                if date.date() == match.date():
                    return find_generic(original_text.lower(), text.lower())

    def find_title(title, text):
        """Method for finding a title field in a text"""
        return find_generic(title.lower(), text.lower())

    try:
        if datatype.lower() in ["author", "date", "title"]:
            return eval("find_{0}(field, text)".format(datatype.lower()))
        else:
            print(
                "*** Warning in standardization.find: {0} not a findable field"
                .format(datatype))
            return find_generic(field, text)
    except Exception as e:
        print("*** Error in standardization.find: {0}".format(e))
        return (-1, -1)


def clean_to_ascii(foreign_char):
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
        'z': ['ž', 'ź', 'ż'],
        'A': ['À', 'Á', 'Â', 'Ä', 'Æ', 'Ã', 'Å', 'Ā'],
        'C': ['Ç', 'Ć', 'Č'],
        'E': ['È', 'É', 'Ê', 'Ë', 'Ē', 'Ė', 'Ę'],
        'I': ['Î', 'Ï', 'Í', 'Ī', 'Į', 'Ì'],
        'L': ['Ł'],
        'N': ['Ñ', 'Ń'],
        'O': ['Ô', 'Ö', 'Ò', 'Ó', 'Œ', 'Ø', 'Ō', 'Õ'],
        'S': ['Ś', 'Š'],
        'U': ['Û', 'Ü', 'Ù', 'Ú', 'Ū'],
        'Y': ['Ÿ'],
        'Z': ['Ž', 'Ź', 'Ż']
    }
    if foreign_char in sum(special_chars.values(), []):
        for k in special_chars:
            if foreign_char in special_chars[k]:
                return k
    print("Can't convert: " + str(foreign_char))
    return ' '
