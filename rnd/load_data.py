import random
import assets

import autociter.core.pipeline as pipeline
from autociter.web.webpages import Webpage
from autociter.utils.decorators import timeout

webpage_data = pipeline.get_wiki_article_links_info(assets.DATA_PATH + "/citations.csv", ['url', 'title'])
labels = links[1]

random_webpage_data = random.sample(webpage_data[0], 100)
source_codes = []

for i, webpage_data in enumerate(random_webpage_data):
	url = webpage_data[labels["url"]]
	print(url)
	try:
		@timeout(15)
		def get_source(url):
			return Webpage(url).source
		source_codes.append(get_source(url))
	except Exception as e:
		print(">>> Error: {0}... Moving on...".format(e))

for i, source_code in enumerate(source_codes):
	indices_of_titles = []
	title = random_webpage_data[labels["title"]]
	offset = 0
	while title in source_code:
		start = source_code.find(title, offset)
		end = start + len(title)
		indices_of_titles.append((start, end))
		offset = end+1

	for title_incident in indices_of_titles:
		# start, end = title_incident
		# min_window_size = 2
		# max_window_size = 20
		# lefts = []
		# rights = []
		# for window_size in range(min_window_size, max_window_size+1):
		# 	left_indices = ()
		# 	lefts.append()
		# lefts = list(set(lefts))
		# rights = list(set(rights))





# print(random_links)

