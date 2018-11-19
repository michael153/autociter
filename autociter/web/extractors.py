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
"""Define objects that extract information from webpages."""
from difflib import SequenceMatcher
from html import unescape

from autociter.data import standardization


def similarity(string1, string2):
    """Return a score representing the similartiy of two strings."""
    return SequenceMatcher(None, string1, string2).ratio()


class ContentExtractor:  #pylint: disable=too-few-public-methods
    """An object that assists with extracting content from webpage."""

    REMOVED_SUBSTRINGS = {"Image\n\n"}

    def __init__(self, webpage):
        """Construct extractor and standardize markdown."""
        self.source = standardization.standardize(webpage.source, "html")
        self.markdown = standardization.standardize(webpage.markdown, "markdown")

    @property
    def title(self):
        """Return the title as defined by the <title> tag."""
        open_tag_start = self.source.find("<title")
        if open_tag_start == -1:
            return ""
        open_tag_end = self.source.find(">", open_tag_start)
        close_tag_start = self.source.find("<", open_tag_end)
        return self.source[open_tag_end + 1: close_tag_start]

    @property
    def open_graph_title(self):
        """Return the title as defined by the <title> tag."""
        open_tag_start = self.source.find("og:title")
        if open_tag_start == -1:
            return ""
        content_start = self.source.find("content=", open_tag_start) + len("content=\"")
        content_end = self.source.find("\"", content_start)
        return self.source[content_start:content_end]

    @property
    def content(self):
        """By default return unchanged markdown."""
        return self.markdown


class TitleFirstContentExtractor(ContentExtractor):
    """Extract content by finding a title and returning everything after.

    >>> extractor = TitleFirstWebpageContentExtractor("Foo\n# Bar\nBaz")
    >>> extractor.find_heading_in_markdown(heading_size=1)
    4
    >>> extractor.retrieve_heading_from_markdown(heading_start_index=4)
    '# Bar'
    >>> extractor.find_title_in_markdown()
    4
    >>> extractor.content
    '# Bar\nBaz'
    """

    IGNORED_HEADINGS = {"", "Search", "News", "Home"}
    CONSIDERED_HEADING_SIZES = {1, 2, 3, 4}

    @property
    def content(self):
        """Retrieve the content of a body of text by looking for a title.

        This method identifies the relevant content by searching the markdown
        for a heading and then returning all of the text after the heading. The
        algorithm works on the assumption that the title of an article is the
        first large heading and that all relevant information occurs after the
        title.
        """
        start_index = self.find_title_in_markdown()
        return self.markdown[start_index:]

    def find_title_in_markdown(self):
        """Predict title and return its index."""

        def retrieve_title_from_heading(heading):
            whitespace_index = heading.find(" ")
            newline_index = heading.find("\n")
            title = heading[whitespace_index + 1:newline_index]
            return title.rstrip().lstrip()

        cached_title = self.open_graph_title or self.title
        candidates = {}
        for heading_size in self.CONSIDERED_HEADING_SIZES:
            current_index = 0
            while self.markdown_contains_heading(
                    heading_size, start=current_index):
                heading_start_index = self.find_heading_in_markdown(
                    heading_size, start=current_index)
                heading = self.retrieve_heading_from_markdown(
                    heading_start_index)
                predicted_title = retrieve_title_from_heading(heading)
                if cached_title:
                    score = similarity(predicted_title, cached_title)
                    if score > 0.95:
                        return heading_start_index
                    candidates[heading_start_index] = score
                elif predicted_title not in self.IGNORED_HEADINGS:
                    return heading_start_index
                heading_prefix = "\n" + "#" * heading_size + " "
                current_index = heading_start_index + len(heading_prefix) + len(
                    heading)
        if not candidates:
            return 0
        winner = max(candidates, key=lambda key: candidates[key])

        return winner if candidates[winner] > 0.2 else 0

    def markdown_contains_heading(self, heading_size, start=0):
        """Return true if the markdown contains a heading of the given size."""
        heading_prefix = "\n" + "#" * heading_size + " "
        for index in range(start, len(self.markdown)):
            substring = self.markdown[index:index + len(heading_prefix)]
            if substring == heading_prefix:
                return True
        return False

    def find_heading_in_markdown(self, heading_size, start=0):
        """Return index of the first heading of the given size."""
        heading_prefix = "\n" + "#" * heading_size + " "
        for index in range(start, len(self.markdown)):
            substring = self.markdown[index:index + len(heading_prefix)]
            if substring == heading_prefix:
                return index + len("\n")
        return -1

    def retrieve_heading_from_markdown(self, heading_start_index):
        """Return a heading located at the given index."""
        assert self.markdown[heading_start_index] == "#", "Invalid start index"
        newline_index = self.markdown.find("\n", heading_start_index)
        return self.markdown[heading_start_index:newline_index]
