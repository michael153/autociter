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
- scikit-learn
- termcolor
- timeoutdecorator
- tensorflow
```pip install dateparser html2text keras PyPDF2 termcolor```

## Open-Ended Questions Regarding Implementation / ML Model
- Would preserving capitalization help the model? (E.g names usually are capitalized or all-caps, titles are usually capitalized)

## G-cloud Compute Engine (Credentials needed)
SSH onto Instance: ```gcloud compute --project "autocitertraining" ssh --zone "us-west1-a" "overpowered-autociter"```

SCP Files to Instance: ```gcloud compute scp --recurse * overpowered-autociter:~/[$PWD]```

SCP Remote Instance Files to Local: ```gcloud compute scp --recurse overpowered-autociter:~/[$PWD]/assets/files/ml assets/files/ml```

## To-do
[Project Guideline Doc](https://docs.google.com/document/d/1TixeELMOJiErqlB_TrHYywdB45SXnI5XN9w0SOLU6vg/edit?usp=sharing)

[Tasklist Spreadsheet](https://docs.google.com/spreadsheets/u/1/d/19hu5XHxxJJhKcj1pjO9ej4refWhLfN44qf1FG3D5WgE/edit?usp=drive_web&ouid=117162895624284967633)
