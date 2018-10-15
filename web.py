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
from urllib import request
from urllib import error


class Crawler:

    num_pages_visited = 0

    def __init__(self, name, opening="<a href=\"", closing="\""):
        self.name = name
        self.opening = opening
        self.closing = closing
        self.data = {}

    def __repr__(self):
        return "Crawler('{0}', '{1}', '{2}')".format(self.name, self.opening,
                                                     self.closing)

    def __str__(self):
        return "Crawler named {0}".format(self.name)

    def search(self, url):
        self.data[url] = Website(url).extract(self.opening, self.closing)
        Crawler.num_pages_visited += 1

    def scrape(self, url):
        try:
            self.search(url)
        except (error.HTTPError, error.URLError, WindowsError):
            self.log(url)

    def saveto(self, filename=None):
        filename = filename or self.name + ".data"
        with open(filename, "a", encoding="utf-8") as file:
            for url in self.data:
                for record in self.data[url]:
                    file.write(record + "\n")

    def log(self, message):
        with open(self.name + ".log", "a", encoding="utf-8") as file:
            file.write(message + "\n")


class Website:

    def __init__(self, url):
        self.url = url
        manager = request.urlopen(url)
        bytecode = manager.read()
        self.source = bytecode.decode("utf-8", "replace")

    def __repr__(self):
        return "Website('{0}')".format(self.url)

    def __str__(self):
        return self.url

    def extract(self, opening, closing):
        strings = []
        left, right, rest = 0, 0, self.source
        while opening in rest and closing in rest:
            left = self.source.find(opening, right)
            right = self.source.find(closing, left)
            strings += [self.source[left:right]]
            rest = self.source[right:]
        return strings
