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

def std_text(text):
	return text.lower()

def std_word(word, data_type):
	"""Standardized text formatting so that words and fields can be properly
	located within a text
	"""
	if data_type == 'authors':
		return word.lower().replace('.', '').replace('-', ' ')
	elif data_type == 'date':
		return word.lower().replace(',', ' ').replace('-', ' ')
	return word

