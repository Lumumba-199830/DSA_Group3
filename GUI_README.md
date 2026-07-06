# Web GUI (added)

This adds a browser-based GUI on top of the existing project **without changing
any of the original files** (`backend.py`, `main.py`, `UI.py`, `SortingModule.py`,
`SystemSearch.py`, `HealthAlertMinHeap.py`, `app.js` are all untouched).

New files only:
- `CAT2_groupwork/server.py` — a small Flask API that reuses `PoultryFarmSystem`
  from `main.py` exactly as the CLI (`UI.py`) does.
- `CAT2_groupwork/templates/index.html` — the web page.
- `CAT2_groupwork/static/style.css` — styling.
- `CAT2_groupwork/static/app.js` — front-end logic (calls the Flask API).
- `CAT2_groupwork/requirements.txt` — the two extra packages needed.

## Run it

```bash
cd CAT2_groupwork
pip install -r requirements.txt
python server.py
```

Then open **http://127.0.0.1:5000** in your browser.

## What you get

- **Registry tab** — table of every bird, search by Tag ID, inline Edit/Delete.
- **Add Bird tab** — form to add a new bird (uses the same `Bird`/`FlockRegistry`
  validation and duplicate-ID checking as the CLI).
- **Sort Flock tab** — sort by weight (quick sort), age, or egg count (merge sort),
  calling the real `SortingModule.sort_flock()`.
- **Health Alert Board** (side panel) — shows the most urgent case from the
  min-heap (`HealthAlertMinHeap`) plus the rest of the alert queue, live.
- **Stat cards** — total birds, healthy/sick/critical counts, total eggs.

The CLI menu in `UI.py` still works exactly as before — this is just an
additional way to use the same backend.