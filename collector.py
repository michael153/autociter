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
"""Define functions that collect data from webpages."""

import sys
import threading

import crawler

GLOBAL_LOCK = threading.Lock()


def main():
    """Build and run several threads that extract data from webpages.

    Given a file containing website URLs, visit each webpage and extract the
    designated elements from the source code. Then, write the data to a file.

    An element is defined as a string (called the content of the element)
    surrounded by a start tag and end tag (also strings).

    Positional Arguments:
        input_filename: The name of a file containing newline-seperated URLs.
        output_filename: The name of the file that will be written to.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: The closing tag of an element (e.g </p>).
    """
    assert len(sys.argv) == 5, "Exactly five command-line arguments expected."
    input_filename, output_filename = sys.argv[1], sys.argv[2]
    start_tag, end_tag = sys.argv[3], sys.argv[4]
    links = retrieve_links(input_filename)
    threads = build_threads(8, links, start_tag, end_tag, output_filename)
    execute_threads(threads)


def retrieve_links(filename):
    """Return URLs saved in a file.

    The specified file should only contain newline-seperated URLs. The function
    may malfunction if the file is formatted incorrectly.

    Arguments:
        filename: The name of a file containing webpage URLs.

    Returns:
        A list of website URLs.
    """
    with open(filename) as file:
        return file.read().splitlines()


def build_threads(num_threads, links, start_tag, end_tag, output_filename):
    """Build threads such that links are evenly devided among processees.

    num_threads should not exceed 8, as more than 8 threads will likely cause
    the request module to throw errors.

    Arguments:
        num_threads: The number of threads to be created.
        links: A list of links that will be split among the threads.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: The closing tag of an element (e.g </p>).
        filename: The name of the file that will be written to.
    """
    threads = []
    for thread_number in range(num_threads):
        assigned_links = allocate_links(thread_number, num_threads, links)
        thread = threading.Thread(
            target=collect_data,
            args=(assigned_links, start_tag, end_tag, output_filename))
        threads.append(thread)
    return threads


def allocate_links(thread_number, num_threads, links):
    """Return the links that the specified thread should visit.

    Arguments:
        thread_number: The numerical identity of a thread.
        num_threads: The total number of threads.
        links: A list of webpage URLs.

    Returns:
        A list of links intended for the specified thread.
    """
    links_per_thread = len(links) // num_threads
    start = thread_number * links_per_thread
    end = start + links_per_thread if thread_number < num_threads - 1 else None
    return links[start:end]


def execute_threads(threads):
    """Start and then join a list of threads."""
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def collect_data(links, start_tag, end_tag, output_filename):
    """Extract elements from websites and save them to a file.

    Arguments:
        links: The URLs of the webpage's to be scraped.
        start_tag: The opening tag of an element (e.g <p>).
        end_tag: The closing tag of an element (e.g </p>).
        filename: The name of the file to be written to.
    """
    for elements in crawler.scrape_websites(links, start_tag, end_tag):
        with GLOBAL_LOCK:
            write_data(elements, output_filename)


def write_data(data, filename, overwrite=False):
    """Write elements of an iterable object to a file.

    Arguments:
        data: An iterable object.
        filename: The name of the file that will be written to.
        overwrite: Whether the file should be overwritten or not.
    """
    mode = "w" if overwrite else "a"
    with open(filename, mode, encoding="utf-8") as file:
        for datum in data:
            file.write(str(datum) + "\n")


if __name__ == "__main__":
    main()
