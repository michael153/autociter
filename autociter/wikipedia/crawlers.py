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

from autociter.wikipedia.extractors import (WikipediaCitationExtractor,
                                            WikipediaArticleExtractor)
from autociter.web.webpages import Webpage, WikipediaArticle


class WikipediaCrawler:  # pylint: disable=too-few-public-methods
    """Scrapes information from Wikipedia webpages.

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
        try:
            return self._scrape(webpage)
        except (error.HTTPError, error.URLError, OSError):
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


class WikipediaArticleCrawler(WikipediaCrawler):
    """Scrapes references from Wikipedia articles."""

    def __init__(self):
        extractors = [
            WikipediaCitationExtractor(variant)
            for variant in WikipediaCitationExtractor.VARIANTS
        ]
        WikipediaCrawler.__init__(self, extractors)

    def scrape(self, webpage):
        """Return references found in an article as Reference objects.

        Arguments:
            webpage: A WikipediaArticle object (or one of its subclasses)

        Returns:
            A list of WikipediaCitation objects.
        """
        return WikipediaCrawler.scrape(self, webpage.edit)


class WikipediaArticleListCrawler(WikipediaCrawler):
    """Scrapes Wikipedia articles from Wikipedia articles.

    Some Wikipedia articles are lists of other articles (e.g the list of
    featured articles). In this case, WikipediaArticleListCrawler can be used to
    retrieve the articles.
    """

    def __init__(self):
        WikipediaCrawler.__init__(self, WikipediaArticleExtractor())

    def scrape(self, webpage):
        """Return articles found in an article as WikipediaArticle objects.

        Arguments:
            webpage: A WikipediaArticle object (or one of its subclasses)

        Returns:
            A list of WikipediaArticle objects.
        """
        return WikipediaCrawler.scrape(self, webpage)
