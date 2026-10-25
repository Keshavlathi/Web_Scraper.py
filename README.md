# Web Scraper

Author: Keshav Lathi

A Python script that scrapes Times of India headlines using `requests` and
Beautiful Soup, then saves them to a timestamped `.txt` file.

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
