# Autociter
Authors: Michael Wan, Balaji Veeramani

## Overview
Uses NLP to accurately extract citation information from any online website

## Dependencies
- termcolor
- boilerpipe
- PyPDF2
- pytz
- date-extractor
- sk-learn
- html2text
- utils
<!-- - datefinder==0.6.1 [(need to manually install zip and change regex==2016.01.10 to regex>=2016.01.10)](https://stackoverflow.com/questions/44016287/error-in-pip-install-datefinder) -->

## Open-Ended Questions Regarding Implementation / ML Model
- Would preserving capitalization help the model? (E.g names usually are capitalized or all-caps, titles are usually capitalized)

## To-do
1. Clean data.txt (remove dead links, remove duplicate entries)
2. Implement custom relevant-article-text-scraper
3. Improve method of finding a field within the article text
4. Write Bash scripts that add autociter/ folder to PYTHONPATH (bash scripts that set environment variables)

## Project Guidelines
[Google Doc](https://docs.google.com/document/d/1TixeELMOJiErqlB_TrHYywdB45SXnI5XN9w0SOLU6vg/edit?usp=sharing)
