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
from html import unescape

from web import Crawler

PARAMETERS = "title", "first", "last", "first1", "last1", "first2", "last2", "publisher", "date", "url", "archive-url"
REQUIRED_FIELDS = "url"


def create(filename, overwrite=False):
    mode = "w" if overwrite else "a"
    with open(filename, mode, encoding="utf-8") as file:
        header = ""
        for parameter in PARAMETERS:
            header += parameter + "\t"
        file.write(header.rstrip() + "\n")


def write(references, filename):
    valid_references = filter(validate, references)
    with open(filename, "a", encoding="utf-8") as file:
        for reference in valid_references:
            file.write(str(reference) + "\n")


def validate(reference):
    if not isinstance(reference, Reference):
        return False
    for parameter in REQUIRED_FIELDS:
        if not parameter in reference:
            return False
    return True


class Article:

    def __init__(self, title):
        self.title = title
        self.url = "https://en.wikipedia.org/wiki/" + title
        self.url_edit = "https://en.wikipedia.org/w/index.php?title=" + title + "&action=edit"

    def __repr__(self):
        return "Article('{0}')".format(self.title)

    def __str__(self):
        return self.url

    @property
    def references(self):
        crawler = Crawler(self.title, "{{cite", "}}")
        crawler.scrape(self.url_edit)
        return [Reference(string) for string in crawler.data[self.url_edit]]


class Reference:

    def __init__(self, string):
        for item in ["\n", "[[", "]]", "&nbsp"]:
            string = string.replace(item, "")
        string = string.replace("''", "\"")
        self.string = unescape(string)

    def __getitem__(self, parameter):
        if parameter in self:
            index_parameter = self.string.find(parameter)
            index_equals = self.string.find("=", index_parameter)
            after_equals = self.string[index_equals + 1:]
            index_item = len(self.string) - len(after_equals.lstrip())
            index_pipe = self.string.find("|", index_item)
            return self.string[index_item:index_pipe].rstrip()
        return ""

    def __contains__(self, parameter):
        index_parameter = self.string.find(parameter)
        index_equals = self.string.find("=", index_parameter)
        index_pipe = self.string.find("|", index_parameter)
        return index_parameter != -1 and index_pipe > index_equals

    def __repr__(self):
        return "Reference('{0}')".format(self.string)

    def __eq__(self, other):
        if not isinstance(other, Reference):
            return False
        return self.string == other.string

    def __str__(self):
        string = ""
        for parameter in PARAMETERS:
            string += self[parameter] + "\t"
        return string.rstrip()
