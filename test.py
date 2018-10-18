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
# Author: Michael Wan <m.wan@berkeley.edu>
"""Test various functions and their practicality / success rate"""


import train
import pipeline

def test_scrapeAuthorInArticle(url_author_pairs):
	"""For a list of url, author pairs, find the success rate of scraping the url and
	finding the authors within the text
	"""
	print("Testing... 'test_scrapeAuthorInArticle'\n\n")
	success = 0
	total = 0
	scrapeFailure = 0
	for u, a in url_author_pairs:
		text = pipeline.getTextFromUrl(u).lower()
		if text == "":
			scrapeFailure += 1
			continue
		convertedAuthorlist = [i.lower().replace('.', '').replace('-', ' ') for i in a]
		value = all([i in text for i in convertedAuthorlist])
		if value == 0:
			print("\nFailed case: {0}\n".format((u, a)))
		success += value
		total += 1
	return (success, total, scrapeFailure)

# urls = ['https://www.nytimes.com/2018/09/25/us/politics/deborah-ramirez-brett-kavanaugh-allegations.html',
		# 'https://www.cnn.com/2018/10/12/middleeast/khashoggi-saudi-turkey-recordings-intl/index.html',
		# 'https://www.huffingtonpost.com/entry/nbc-news-trump-robert-e-lee_us_5bc3813de4b0bd9ed55b2eda']

# authors = [['Stephanie Saul', 'Robin Pogrebin', 'Mike McIntire', 'Ben Protess'],
		   # ['Laura Smith-Spark', 'Nic Robertson'], # Need to omit '-' to work
		   # ['Hayley Miller']]

t_res = test_scrapeAuthorInArticle(pipeline.getArticleUrlAuthors('assets/data.txt')[:50])
print("{0}/{1} ({3}%) cases passed, {2} scrapes threw errors".format(t_res[0], t_res[1], t_res[2], (100.0*t_res[0])/t_res[1]))


