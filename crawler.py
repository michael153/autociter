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
"""Define functions that help with webpage data extraction."""

from urllib import request
from urllib import error
import html
import time


class Element:
    """An element represents a string enclosed by two tags."""

    def __init__(self, start_tag, content, end_tag):
        """Create an instance of element.

        Newline characters and HTML character references are removed from the
        content of the element on creation.

        Arguments:
            start_tag: The opening tag of an element (e.g <p>).
            content: The string enclosed by the tags (e.g "Hello world!")
            end_tag: The closing tag of an element (e.g </p>).
        """
        self.start_tag = start_tag
        self.content = content
        self.end_tag = end_tag
        Element.format(self)

    def __repr__(self):
        return "Element({0}, {1}, {2})".format(self.start_tag, self.content,
                                               self.end_tag)

    def __str__(self):
        return self.start_tag + self.content + self.end_tag

    def format(self):
        """Remove newlines and HTML character references from content."""
        self.content = html.unescape(self.content.replace("\n", ""))


def scrape_websites(links, start_tag, end_tag):
    """Scrape webpages for elements defined by the given tags.

    If a webpage is unable to be reached, the URL of that webpage is written to
    "log.txt", and no elements are extracted from that webpage.

    Arguments:
        links: The URLs of the webpage's to be scraped.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: The closing tag of an element (e.g </p>).

    Yields:
        A list of element objects.
    """
    for link in links:
        source_code = retrieve_source_code(link)
        yield extract_elements(source_code, start_tag, end_tag)


def extract_elements(text, start_tag, end_tag):
    """Return elements found in a body of text.

    Arguments:
        text: The string to be searched.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: the closing tag of an element (e.g </p>).

    Returns:
        A list of element objects.
    """
    left, right = 0, 0
    elements = []
    while start_tag in text[right:]:
        left = text.find(start_tag, right)
        right = text.find(end_tag, left) + len(end_tag)
        content = text[left + len(start_tag):right - len(end_tag)]
        elements += [Element(start_tag, content, end_tag)]
    return elements


def retrieve_source_code(link):
    """Retrieve a webpage's source code.

    HTML character references (e.g &gt;, &#62;, &#x3e;) are left intact. If the
    link is inaccessible, the URL is written to the file "log.txt" and an empty
    string is returned.

    Arguments:
        link: The webpage's URL.

    Returns:
        A string representing the source code of a webpage.
    """
    try:
        website = _open_website(link)
        byte_code = _read_website(website)
        return byte_code.decode("utf-8", "replace")
    except RuntimeError:
        log(link)
        return ""


def _open_website(link, num_attempts=0):
    """Open the given URL and return a context manager object.

    The source code of a webpage can be retrieved by reading and then
    decoding the returned context manager object. If the URL fails to
    open, the function waits one second and then tries again.

    Arguments:
        link: The webpage's URL.

    Returns:
        A context manager object.

    Raises:
        RuntimeError if more than ten attempts are made.
    """
    if num_attempts > 10:
        raise RuntimeError("Too many attempts to open website.")
    try:
        return request.urlopen(link)
    except (WindowsError, error.URLError, error.HTTPError):
        time.sleep(1)
        return _open_website(link, num_attempts + 1)


def _read_website(website, num_attempts=0):
    """Read the given context manager object and return bytecode.

    website is a context manager object constructed by the request module. The
    object can be read and then decoded to retrieve a webpage's source code. If
    an error occurs, the function waits one second before trying again.

    Arguments:
        website: A context manager object returned by urlopen.

    Returns:
        The webpage's bytecode.

    Raises:
        RuntimeError if more than ten attempts are made.
    """
    if num_attempts > 10:
        raise RuntimeError("Too many attempts to read website.")
    try:
        return website.read()
    except (WindowsError, error.URLError, error.HTTPError):
        time.sleep(1)
        return _read_website(website, num_attempts + 1)


def log(message, filename="log.txt"):
    """Write a message to a file.

    Arguments:
        message: The message to be logged.
        exception: An error that will be printed to the console.
        filename: The name of the file that will be written to.
    """
    with open(filename, "a", encoding="utf-8") as file:
        file.write(message)
