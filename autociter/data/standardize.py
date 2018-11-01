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
"""Library that provides method to standardize certain words so they can properly
located within a text"""

from autociter.data.storage import Table, Record
import autociter.data.queries as queries

def std_table(table):
	std_fields = ["title", "author", "publisher", "date", "url", "archive-url"]
	ret = Table(fields=std_fields)
	for rec in table.records:
		author_fields = [("first", "last"), ("first1", "last1"), ("first2", "last2")]
		authors = []
		for i in author_fields:
			author = (rec[i[0]] + " " + rec[i[1]]).strip()
			if author != "":
				authors.append(author)
		values = []
		for attr in std_fields:
			if queries.contains(attr)(rec):
				values.append(rec[attr])
			elif attr == 'author':
				values.append(list(set(authors)))
			else:
				values.append("")
		ret.add(Record(std_fields, values))
	return ret

def std_text(text):
	return text.lower()

def std_data(data, data_type):
	"""Standardized text formatting so that words and fields can be properly
	located within a text
	"""
	if data_type == 'author':
		return [d.lower().replace('.', '').replace('-', ' ') for d in data]
	elif data_type == 'date':
		return data.lower().replace(',', ' ').replace('-', ' ')
	elif data_type == 'title':
		return data.title()
	return data
