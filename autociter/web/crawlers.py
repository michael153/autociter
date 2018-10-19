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
"""Define Crawler objects."""
from urllib import error

from extractors import ReferenceExtractor1, ReferenceExtractor2, ArticleExtractor
from webpages import Webpage, Article


#pylint: disable=too-few-public-methods
class Crawler:
    """Scrapes information from webpages.

    Crawlers are used to collect data from webpages. The type of data of
    collected depends on which extractors are passed in.

    Arguments:
        *extractors: The extractor objects used for scraping.
    """

    def __init__(self, *extractors):
        self.extractors = extractors

    def scrape(self, webpage):
        """Safely scrape a webpage.

        Arguments:
            webpage: A Webpage object (or one of its subclasses).

        Returns:
            Scraped data if no errors occurred, otherwise an empty list.
        """
        assert isinstance(webpage, Webpage), "Expected Webpage object."
        try:
            return self._scrape(webpage)
        except (error.HTTPError, error.URLError, WindowsError):
            return []

    def _scrape(self, webpage):
        """Scrape a webpage.

        The extract method of each extractor is applied to the webpage's
        source code. The resulting data is returned.
        """
        data = []
        for extractor in self.extractors:
            data += extractor.extract(webpage.source)
        return data


class ArticleCrawler(Crawler):
    """Scrapes references from Wikipedia articles."""

    def __init__(self):
        Crawler.__init__(self, ReferenceExtractor1(), ReferenceExtractor2())

    def scrape(self, webpage):
        """Return references found in an article as Reference objects.

        Arguments:
            webpage: An Article object (or one of its subclasses)

        Returns:
            A list of Reference objects.
        """
        assert isinstance(webpage, Article), "Expected Article object."
        return Crawler.scrape(self, webpage.edit)


class ArticleListCrawler(Crawler):
    """Scrapes Wikipedia articles from Wikipedia articles.

    Some Wikipedia articles are lists of other articles (e.g the list of
    featured articles). In this case, ArticleListCrawler can be used to
    retrieve the articles.
    """

    def __init__(self):
        Crawler.__init__(self, ArticleExtractor())

    def scrape(self, webpage):
        """Return articles found in an article as Article objects.

        Arguments:
            webpage: An Article object (or one of its subclasses)

        Returns:
            A list of Article objects.
        """
        assert isinstance(webpage, Article), "Expected Article object."
        return Crawler.scrape(self, webpage)
