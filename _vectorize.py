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
"""Some random bullshit I was experimenting for word vectorization, but I'm not planning on using it (just leaving it here for future reference)"""

import re
from bs4 import BeautifulSoup
import gensim
import nltk
import numpy as np
from requests import get
from sklearn.decomposition import PCA
from matplotlib import pyplot
from pattern.web import plaintext


def split_into_sentences(text):
	# https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
	caps = "([A-Z])"
	prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
	suffixes = "(Inc|Ltd|Jr|Sr|Co)"
	starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
	acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
	websites = "[.](com|net|org|io|gov)"
	text = " " + text + "  "
	text = text.replace("\n"," ")
	text = re.sub(prefixes,"\\1<prd>",text)
	text = re.sub(websites,"<prd>\\1",text)
	if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
	text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
	text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
	text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
	text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
	text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
	text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
	text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
	if "”" in text: text = text.replace(".”","”.")
	if "\"" in text: text = text.replace(".\"","\".")
	if "!" in text: text = text.replace("!\"","\"!")
	if "?" in text: text = text.replace("?\"","\"?")
	text = text.replace(".",".<stop>")
	text = text.replace("?","?<stop>")
	text = text.replace("!","!<stop>")
	text = text.replace("<prd>",".")
	sentences = text.split("<stop>")
	sentences = sentences[:-1]
	sentences = [s.strip() for s in sentences]
	return sentences


def graphVectorizedWords(X):
	pca = PCA(n_components=2)
	result = pca.fit_transform(X)
	pyplot.scatter(result[:, 0], result[:, 1])
	for i, word in enumerate(words):
		pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
	pyplot.show()


def getTextFromLink(url):
	html = get(url).text
	texts = plaintext(html)
	sentences = split_into_sentences(texts)
	# https://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
	words = []
	for sentence in sentences:
		words.append(re.findall(r"[\w']+|[.,!?;]", sentence))
	return words


random_article_links = ['https://www.nytimes.com/2018/10/04/us/politics/trump-kavanaugh-midterm-elections.html',
	'https://www.nytimes.com/2018/10/04/us/politics/brett-kavanaugh-supreme-court.html',
	'https://www.cnn.com/2018/10/05/politics/brett-kavanaugh-donald-trump-republicans-vote/index.html',
	'https://www.msn.com/en-us/sports/nfl/brady-reaches-500-td-passes-in-patriots-38-24-win/ar-BBNXIxS',
	'http://www.nationalgalleryimages.co.uk/search.aspx?q=HOGARTH%2c+William&amp%3bmode=artist&amp%3bstart=15&amp%3bnum=12&amp%3bng=NG117&amp&frm=1',
	'https://jerz.setonhill.edu/design/WTC/index.html',
	'https://www.rcseng.ac.uk/about-the-rcs/',
	'https://www.nbcnews.com/politics/supreme-court/cloud-legitimacy-crisis-taint-legal-experts-kavanaugh-joining-court-n916731',
	'https://www.bbc.com/news/world-latin-america-45780176',
	'https://www.antaranews.com/berita/755975/hasil-dan-klasemen-liga-spanyol-sevilla-ambil-alih-posisi-puncak',
	'https://abcnews.go.com/US/wireStory/mormon-leader-nicknames-faith-victory-satan-58346683',
	'http://www.artoftheprint.com/artistpages/hogarth_william_evening.htm',
	'http://modernhistoryproject.org/mhp?Article=WallStHitler&C=2',
	'http://www.victorianlondon.org/publications/pleasuregardens-6-saddlerswells.htm'
	]

sentences = []

for i in random_article_links:
	sentences += getTextFromLink(i)

model = gensim.models.Word2Vec(sentences, min_count=1, size=75, alpha=0.2)
print(model)

words = list(model.wv.vocab)
X = model[model.wv.vocab]

print(words)
print("\n\n\n")

result = model.most_similar(positive=['Kavanaugh'], topn=20)
print(result)

# print(words)
