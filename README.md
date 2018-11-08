# Autociter
Authors: Michael Wan, Balaji Veeramani

## Overview
Uses NLP to accurately extract citation information from any online website

## Dependencies
- dateparser
- html2text
- keras
- numpy
- PyPDF2
- pytz
- scikit-learn
- termcolor
- tensorflow

## Open-Ended Questions Regarding Implementation / ML Model
- Would preserving capitalization help the model? (E.g names usually are capitalized or all-caps, titles are usually capitalized)

## To-do
See spreadsheet

## G-cloud
SSH: ```gcloud compute --project "autocitertraining" ssh --zone "us-west1-a" "overpowered-autociter"```

SCP Files: ```gcloud compute scp --recurse * overpowered-autociter:~/[$PWD]```


[Google Doc](https://docs.google.com/document/d/1TixeELMOJiErqlB_TrHYywdB45SXnI5XN9w0SOLU6vg/edit?usp=sharing)
