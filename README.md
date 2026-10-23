# Lucky Draw — Random Name Picker

A small, dependency-free Python web app that picks a random name from a list. Add one name per line, click **Pick a name**, and the page counts down from five before revealing the selection.

## Run locally

Requires Python 3.9 or newer. From this folder, run:

```powershell
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Press `Ctrl+C` in the terminal to stop the server.

The picker accepts 1–500 names, trims surrounding whitespace, and allows duplicate names. Names are selected on the server after the countdown completes.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
