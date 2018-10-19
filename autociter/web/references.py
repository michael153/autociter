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
"""Define reference objects."""
import html


def clean(string):
    """Remove or replace unexpected sequences."""
    for item in ["\n", "[[", "]]", "&nbsp"]:
        string = string.replace(item, "")
    string = string.replace("''", "\"")
    return html.unescape(string)


class ArticleReference:
    """A Wikipedia article reference."""

    ATTRIBUTES = ("title", "first", "last", "first1", "last1", "first2",
                  "last2", "publisher", "date", "url", "archive-url")

    ASSIGNER, DELIMITER = "=", "|"

    def __init__(self, string):
        """Initialize article reference.

        Arguments:
            string: A raw article reference.
        """
        self.string, self.data = clean(string), {}
        self.assigner, self.delimiter = "=", "|"
        for attribute in ArticleReference.ATTRIBUTES:
            self.data[attribute] = self.find(attribute, self.string)

    def find(self, attribute, string):
        """Find attribute value in a raw article citation.

        Arguments:
            attribute: A string representing the name of an attribute.

        Returns:
            The value of the attribute, if present, else an empty string.
        """
        attribute_index = string.find(attribute)
        if attribute_index == -1:
            return ""
        assigner_index = string.find(self.ASSIGNER, attribute_index)
        delimiter_index = string.find(self.DELIMITER, attribute_index)
        if assigner_index > delimiter_index:
            rest = string[attribute_index + len(attribute):]
            return self.find(attribute, rest)
        after_assigner = string[assigner_index + 1:]
        # Finds index of first nonwhitespace character after assigner
        value_index = len(string) - len(after_assigner.lstrip())
        return string[value_index:delimiter_index].rstrip()

    def __getitem__(self, attribute):
        return self.data[attribute]

    def __contains__(self, attribute):
        return self.data[attribute] != ""

    def __str__(self):
        """Return csv-compatible representation."""
        string = ""
        for attribute in ArticleReference.ATTRIBUTES:
            string += self.data[attribute] + "\t"
        return string.rstrip()
