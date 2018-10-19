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
"""Define functions for collecting Wikipedia reference data."""
import threading

from autociter.data.processor import create, write

from autociter.web.webpages import Article
from autociter.web.crawlers import ArticleCrawler
from autociter.web.references import ArticleReference

GLOBAL_LOCK = threading.Lock()
FILENAME = "data.txt"


#TODO: Restructure all of this
def aggregate(filename):
    """Aggregate Wikipedia article data (multithreaded).

    Arguments:
        input_file: The path of a file containing newline-seperated article titles.
        output_filename: The path of the desired output data file.
    """
    titles = lines(filename)
    articles = [Article(title) for title in titles]
    threads = build(8, _aggregate, articles)
    attributes = ArticleReference.ATTRIBUTES
    create(FILENAME, attributes)
    execute(threads)


def _aggregate(*articles):
    """Write reference data collected from a list of articles."""
    crawler = ArticleCrawler()
    for article in articles:
        cached = crawler.scrape(article)
        with GLOBAL_LOCK:
            write(cached, FILENAME)


def lines(filename):
    """Return newline-seperated lines of a file."""
    with open(filename) as file:
        return file.read().splitlines()


def build(num_threads, target, args):
    """Create threads for multi-threaded aggregation.

    Arguments:
        num_threads: The number of threads.
        target: The function that each thread will execute.
        args: The arguments that will be passed into target.

    Returns:
        A list of threads.
    """
    threads = []
    for thread_number in range(num_threads):
        assigned_args = allocate(args, thread_number, num_threads)
        thread = threading.Thread(target=target, args=assigned_args)
        threads.append(thread)
    return threads


def allocate(args, thread_number, num_threads):
    """Split arguments among threads."""
    args_per_thread = len(args) // num_threads
    start = thread_number * args_per_thread
    end = start + args_per_thread if thread_number < num_threads - 1 else None
    return args[start:end]


def execute(threads):
    """Start then join threads."""
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
