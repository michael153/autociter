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
import crawler

HEADERS = ("title", "first", "last", "publisher", "date", "url")
REQUIRED = ("title", "url")

def generate_references(filename):
    with open(filename, encoding="utf-8") as file:
        strings = file.read().splitlines()
        references = []
        for string in strings:
            references += [Reference(string)]
        return references

class Article:

    def __init__(self, title):
        self.title = title
        self.url = "https://en.wikipedia.org/wiki/" + title
        self.url_edit = "https://en.wikipedia.org/w/index.php?title=" + title + "&action=edit"

def write_to_csv(references, filename="asdf.csv", delimiter="\t"):
    with open(filename, "w", encoding="utf-8") as file:
        for reference in references:
            file.write(str(reference) + "\n")

class Reference:

    def __init__(self, content):
        self.content = content
        self.remove(["\n", "[[", "]]"])
        self.content.replace("''", "\"")

    def __getitem__(self, parameter):
        if parameter in self:
            index_parameter = self.content.find(parameter)
            index_equals = self.content.find("=", index_parameter)
            after_equals = self.content[index_equals + 1:]
            index_argument = len(self.content) - len(after_equals.lstrip())
            index_pipe = self.content.find("|", index_argument)
            return self.content[index_argument:index_pipe].rstrip()
        else:
            return ""

    def __contains__(self, parameter):
        index_parameter = self.content.find(parameter)
        index_equals = self.content.find("=", index_parameter)
        index_pipe = self.content.find("|", index_parameter)
        return index_parameter != -1 and index_pipe > index_equals

    def __str__(self, delimiter="\t", parameters=HEADERS):
        string = ""
        for parameter in parameters:
            string += self[parameter] + delimiter
        return string.rstrip()[:-len(delimiter)]

    def __repr__(self):
        return "Reference('{0}')".format(self.content)

    def remove(self, substrings):
        """Remove substrings from a reference.

        Arguments:
            substrings: A list of strings to be removed.
        """
        for substring in substrings:
            self.content = self.content.replace(substring, "")

r = generate_references("references.txt")
write_to_csv([ree for ree in r if all([ree[par] for par in REQUIRED])])
