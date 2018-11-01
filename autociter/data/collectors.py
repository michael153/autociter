import threading

from autociter.citation.references import ArticleReference

"""
def aggregate(filename):
    """Aggregate Wikipedia article data (multithreaded).

    Arguments:
        input_file: The path of a file containing newline-seperated article titles.
        output_filename: The path of the desired output data file.
    """
    titles = lines(filename)
    create(FILENAME, attributes)


class ArticleRefernceCollector:

    def aggregate(self, articles):
        articles = [Article(title) for title in items]
        threads = multithreading.build(8, self.collect, articles)
        self.table = Table(fields=ArticleReference.ATTRIBUTES)
        multithreading.execute(threads)

def aggregate(*articles):
    """Write reference data collected from a list of articles."""
    crawler = ArticleCrawler()
    for article in articles:
        cached = crawler.scrape(article)
        with multithreading.GLOBAL_LOCK:
            self.table.add(Refer)

"""
