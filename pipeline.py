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
"""Data pipeline file that extracts and prepares data for analysis"""

import re
import json
import time
import os.path
import database
from boilerpipe.extract import Extractor

def getTextFromUrl(url):
	"""Preliminary method to extract only the relevant article text from a website using the
	Python-Boilerpipe API (https://github.com/misja/python-boilerpipe)

	The extractor accurately finds a start of the article, but because it omits divs with short text lengths,
	we must manually get the article (including author) text

	Alternates:
	https://github.com/goose3/goose3

	Misc. References:
	https://stackoverflow.com/questions/4576077/python-split-text-on-sentences

	Failed cases:
	https://www.bbc.com/sport/football/22787925, ['Alasdair Lamont']
	"""
	startTime = time.time()
	if ".pdf" in url:
		try:
			r = requests.get(url, stream=True)
			f = io.BytesIO(r.content)
			reader = PdfFileReader(f)
			contents = reader.getPage(pageNumber).extractText()
			extractedWords = re.sub("[^\w]", " ", contents).split()
			return ' '.join(extractedWords)
		except:
			print(">>> Error: Error reading pdf in getTextFromUrl")
			return ""
	try:
		cleanedText = Extractor(extractor='CanolaExtractor', url=url).getText()
		allText = Extractor(extractor='KeepEverythingExtractor', url=url).getText()
		# Remove \n and special characters via regex
		extractedWords = re.sub("[^\w]", " ", cleanedText).split()
		totalWords = re.sub("[^\w]", " ", allText).split()
		# Try three (arbitrary amount) of the starting words in extractedWords
		for i in range(3):
			if extractedWords[i] in totalWords:
				totalWords = totalWords[totalWords.index(extractedWords[i]):]
				break
		# Try three (arbitrary amount) of the ending words in extractedWords
		for i in range(1, 4):
			if extractedWords[-i] in totalWords:
				reverseLookupIndex = len(totalWords) - 1 - totalWords[::-1].index(extractedWords[-i])
				totalWords = totalWords[:reverseLookupIndex]
				break
		print("Text scrape successfully finished in {0} seconds".format(time.time() - startTime))
		return ' '.join(totalWords)
	except:
		print(">>> Error: Error reading text in getTextFromUrl")
		return ""

def getArticleInfo(file, args):
	"""Retrieve article information from wikipedia database Tables, and store
	data into a tupled list

	>>> getArticleInfo('asserts/data.txt', ['url', 'author'])
	"""

	def getAttribute(r, arg):
		"""Given a row entry in Table r, return the proper value in the table that
		corresponds to the argument arg

		>>> getAttribute(t[0], "url")
		'http://www.iwm.org.uk/memorials/item/memorial/2814'
		"""
		if arg in ['title', 'publisher', 'date', 'url', 'archive-url']:
			return r[arg]
		elif arg == 'authors':
			tempList = [(r["first"], r["last"]), (r["first1"], r["last1"]), (r["first2"], r["last2"])]
			standardizeAuthorName = lambda x: x[0].strip() not in ["", "null"] and x[1].strip() not in ["", "null"]
			return list(set([' '.join(a) for a in tempList if standardizeAuthorName(a)]))

	t = database.Table(file)
	data = [[] for i in range(len(args))]
	# Prepare urls and authors
	for r in t.records:
		assureValidity = lambda x: getAttribute(x, 'url') not in ["", [], "null"] #Make sure that url is valid for each table entry
		# assureValidity = lambda x: all([getAttribute(x, arg) not in ["", [], "null"] for arg in args]) #Make sure that all datapoints are valid for each table entry
		if assureValidity(r):
			for i in range(len(args)):
				arg = args[i]
				data[i].append(getAttribute(r, arg))
	datapoints = list(zip(*data))
	# Return labels in order to remember what each index in a datapoint represents
	labels = {args[x]: x for x in range(len(args))}
	return (datapoints, labels)

def saveData(fileName, data):
	"""Given a fileName and data, a list of tuples containing url link, list of citation info,
	create an entry in the dict in savedArticleData.dat
	"""
	if not os.path.isfile(fileName):
		f = open(fileName, "w+")
		f.write('{}')
		f.close()
	try:
		savedDict = json.load(open(fileName))
	except:
		savedDict = {}
	for datapoint in data:
		savedDict[datapoint['url']] = {}
		for keys, val in datapoint['citation_info'].items():
			savedDict[datapoint['url']][keys] = val
		savedDict[datapoint['url']]['article_oneHot'] = datapoint['article_oneHot']
	with open(fileName, 'w') as out:
		json.dump(savedDict, out, sort_keys=True, indent=4)

def cleanToAscii(c):
	"""Converts a non-ASCII character into it's ASCII equivalent

		>>> cleanToAscii('ç')
		'c'
	"""
	specialCharacters = {
		'a': ['à', 'á', 'â', 'ä', 'æ', 'ã', 'å', 'ā'],
		'c': ['ç', 'ć', 'č'],
		'e': ['è', 'é', 'ê', 'ë', 'ē', 'ė', 'ę'],
		'i': ['î', 'ï', 'í', 'ī', 'į', 'ì'],
		'l': ['ł'],
		'n': ['ñ', 'ń'],
		'o': ['ô', 'ö', 'ò', 'ó', 'œ', 'ø', 'ō', 'õ'],
		's': ['ß', 'ś', 'š'],
		'u': ['û', 'ü', 'ù', 'ú', 'ū'],
		'y': ['ÿ'],
		'z': ['ž', 'ź', 'ż']
	}
	if c in sum(specialCharacters.values(), []):
		for k in specialCharacters.keys():
			if c in specialCharacters[k]:
				return k
	else:
		print("Can't convert: " + str(c))
		return ' '

def oneHot(s):
	"""Converts a string s into a one-hot encoded vector with default dimensions of 600 by 65.
	   The column vector will correspond to ['A', 'B', ... 'Z', 'a', 'b', ... 'z', 0, 1, ... 9, '-', ':', '.']

	   Arguments:
	   		s: A string s that represents the first and last characters of an article / text
	   		   with dimensions (600, 1)
	"""
	encodingRange = 65
	mat = [[0 for _ in range(encodingRange)] for __ in range(len(s))]
	for i in range(len(s)):
		char = s[i]
		if not (ord(char) < 127 and ord(char) > 31):
			char = cleanToAscii(char)
		if char.isupper():
			mat[i][ord(char) - 65] = 1
		elif char.islower():
			mat[i][26 + ord(char) - 97] = 1
		elif char.isnumeric():
			mat[i][52 + ord(char) - 48] = 1
		elif char == '-':
			mat[i][encodingRange-3] = 1
		elif char == ':':
			mat[i][encodingRange-2] = 1
		elif char == '.':
			mat[i][encodingRange-1] = 1
	return mat

def vectorizeText(text, charLen=600):
	"""Given a string of text, convert into a padded / truncated matrix of one hot vectors"""

	def truncateText(text, textLen=600):
		"""Truncates a text so that the return value has a length of textLen by taking the first
		and last characters
		"""
		if len(text) > textLen:
			odd = (textLen % 2)
			return text[0:textLen//2] + text[-(textLen + odd)//2:]
		else:
			return text
	def padText(text, textLen=600):
		"""Pads a text with space characters in the middle to preserve the beginning and ending
		while also so that the length of the text is equal to textLen
		"""
		if len(text) < textLen:
			curLen = len(text)
			remainder = textLen - curLen
			return text[:curLen//2] + (' ')*remainder + textLen[curLen//2:]
		else:
			return text
	
	try:
		if len(text) > charLen:
			text = truncateText(text, charLen)
		elif len(text) < charLen:
			text = padText(text, charLen)
		return oneHot(text)
	except:
		print("\n>>> Error: Vectorizing Text\n\n" + str(text) + "\n")
		return ""

info = getArticleInfo('assets/data.txt', ['url', 'authors'])
datapoints, labelLookup = info[0], info[1]

data = []
for entry in datapoints[:25]:
	url = entry[labelLookup['url']]
	authors = entry[1]
	citation_info = {x: entry[labelLookup[x]] for x in labelLookup.keys()}
	text = getTextFromUrl(url)
	if text != "":
		v = vectorizeText(text)
		if v != "":
			d = {'url': url, 'citation_info': {}, 'article_oneHot': str(v)}
			for k in citation_info.keys():
				d['citation_info'][k] = citation_info[k]
			data.append(d)

saveData('assets/savedArticleData.dat', data)


