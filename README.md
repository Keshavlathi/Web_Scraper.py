# Web Scraper

Author: Keshav Lathi

A Python script that fetches current article headlines from Times of India and
Hindustan Times, then saves them to a timestamped CSV file with the publisher,
headline, article link, and fetch time.

## Setup

From this folder, create and activate a virtual environment, then install the
project dependencies:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

In VS Code, select the `.venv` interpreter for this workspace so Pylance can
resolve the installed packages.

## Run

```powershell
python newsheadlines.py
```

The script fetches both publishers each time it runs and saves the CSV in this
project folder. If one publisher is unavailable, it reports the error and saves
the results from the other publisher when possible. It does not run continuously
or send alerts.

## Test

```powershell
python -m unittest
```
