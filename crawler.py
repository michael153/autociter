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
"""Define functions that help with webpage data exctraction."""

from urllib import request


def extract_elements(text, start_tag, end_tag):
    """Return elements in a body of text.

    An element is defined as a string (called the content of the element)
    surrounded by a start tag and end tag (also strings).

    Arguments:
        text: The string to be searched.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: the closing tag of an element (e.g </p>).

    Returns:
        A list of elements defined by the given tags.
    """
    left, right = 0, 0
    elements = []
    while start_tag in text[right:]:
        left = text.find(start_tag, right)
        right = text.find(end_tag, left) + len(end_tag)
        elements.append(text[left:right])
    return elements


def retrieve_source_code(link):
    """Retrieve a webpage's source code.

    HTML character references (e.g &gt;, &#62;, &#x3e;) are left intact.

    Arguments:
        link: The webpage's URL.

    Returns:
        A string representing the source code of a webpage.
    """
    website = request.urlopen(link)
    byte_code = website.read()
    return byte_code.decode("utf-8", "replace")


def scrape_websites(links, start_tag, end_tag):
    """Scrapes webpages for elements defined by the given tags.

    Arguments:
        links: The URLs of the webpage's to be scraped.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: The closing tag of an element (e.g </p>).

    Returns:
        A list of elements defined by the given tags.
    """
    elements = []
    num_links_visited, num_elements_extracted = 0, 0
    for link in links:
        source_code = retrieve_source_code(link)
        num_links_visited += 1
        elements = extract_elements(source_code, start_tag, end_tag)
        num_elements_extracted += len(elements)
        print(num_links_visited, "\t", num_elements_extracted, "\t", link)
    return elements
