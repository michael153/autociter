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
import threading

from wikipedia import Article, write, create
from web import Crawler

INPUT_FILE = "assets/featured.txt"
OUTPUT_FILE = "assets/data.txt"
GLOBAL_LOCK = threading.Lock()
NUM_ARTICLES = 5839


def main():
    titles = lines(INPUT_FILE)
    articles = [Article(title) for title in titles]
    threads = build(8, aggregate, articles)
    create(OUTPUT_FILE)
    execute(threads)


def lines(filename):
    with open(filename) as file:
        return file.read().splitlines()


def build(num_threads, target, args):
    threads = []
    for thread_number in range(num_threads):
        assigned_args = allocate(args, thread_number, num_threads)
        thread = threading.Thread(target=target, args=assigned_args)
        threads.append(thread)
    return threads


def allocate(args, thread_number, num_threads):
    args_per_thread = len(args) // num_threads
    start = thread_number * args_per_thread
    end = start + args_per_thread if thread_number < num_threads - 1 else None
    return args[start:end]


def execute(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def aggregate(*articles):
    for article in articles:
        cached = article.references
        with GLOBAL_LOCK:
            write(cached, OUTPUT_FILE)
            debug(article)


def debug(article):
    progress = Crawler.num_pages_visited / NUM_ARTICLES
    percent_complete = str(round(100 * progress, 2)) + "%"
    print("{0}\t{1}".format(percent_complete, article.url))


if __name__ == "__main__":
    main()
