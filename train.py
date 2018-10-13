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
"""(As of now) Defines methods to convert web-scraped text into one-hot encodings to be passed into a model."""

import re
from requests import get
from pattern.web import plaintext

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

def getTextFromUrl(url):
	"""Preliminary method for retrieving relevant text from a website url

		Misc. references:
			https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
	"""

	def splitIntoSentences(text):
		"""Splits a text into a list of sentences based on the English grammar"""
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

	html = get(url).text
	texts = plaintext(html)
	sentences = splitIntoSentences(texts)
	words = ""
	for sentence in sentences:
		for word in re.findall(r"[\w']+|[.,!?;]", sentence):
			words += word + " "
	return words

def formatRawText(text, charLen=600):
	"""Given a string of text, convert into a padded / truncated matrix of one hot vectors"""
	if len(text) > charLen:
		text = truncateText(text, charLen)
	elif len(text) < charLen:
		text = padText(text, charLen)
	return oneHot(text)


arbitaryUrl = 'https://www.cnn.com/2018/10/12/middleeast/khashoggi-saudi-turkey-recordings-intl/index.html'
print(formatRawText(getTextFromUrl(arbitaryUrl)))
