# Datadog Monitoring Project

This project allows the bid syncing between Adwords keywords.

## Getting Started

This is a beta project, to be used as an experiment. Follow the simple instructions below to install.

### Prerequisites

All the code runs in python. Here are the needed dependencies:

```
- Google Ads python lib (pull from https://github.com/googleads/googleads-python-lib)
- Google API client lib - for Spreadsheet use (pip install)
- httplib2 (pip install)
- multiprocessing (pip install)
- json (pip install)
```

### Running


```
python main.py
```


## Running the tests

Tests will be available in the next few days

## How it works

1) The script first pulls all dummy placeholders and their bid. It does so by crawling the dummy placeholders from the manual accounts and keeping a dictionnary of their according synced bid.
2) Then the script creates the dictionnary of the actual keywords that will need a bid update. It iterates through all the keywords in manual PG account, matches the according dummy placeholders and keeps track of the keyword location, text and new bid.
3) The script finally updates the keywords, in batches of 2k at a time (Google limit)


## Author

* **Xavier Green** - *Amazon FR Paid Search Team*
