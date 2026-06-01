# Sam Sulek Lifting Tracking

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://samsulekliftingtracking.streamlit.app/)

Scrapes Sam Sulek's YouTube uploads ([@sam_sulek](https://www.youtube.com/@sam_sulek), channel `UCAuk798iHprjTtwlClkFxMA`), derives the muscle group(s), lifting phase and day number from each video title, and presents the result as a Streamlit app: muscle-group pie charts, phase durations and per-lift calendar heatmaps. New videos are pulled automatically once a day by a GitHub Action.

Live app: <https://samsulekliftingtracking.streamlit.app/>

## Contents

| Path | What it does |
|---|---|
| `main.py` | Streamlit app. Loads `video_data_final.json`; "Get Most Recent Data" button scrapes new videos (via `scrape.py`); "Analyse" button renders the pie charts, phase durations and calendars. |
| `api_scraper.py` | **Primary ingestion.** Pulls the full upload list via the YouTube Data API, enriches only new videos with `analyse.clean_and_enrich_json`, prepends them to `video_data_final.json`. Run by the daily Action. Needs `YT_API_KEY`. |
| `scrape.py` | yt-dlp scraper used by the Streamlit "Get Most Recent Data" button. `get_date_for_video` reads upload dates and expects a `cookies.txt` (see TODOs). |
| `analyse.py` | Title cleaning + enrichment (`clean_and_enrich_json`), event/day parsing (`parse_event_day`, `PHASE_DICT`, `VALID_EVENTS`) and stats aggregation (`get_current_stats`). |
| `muscle_parser.py` | Keyword-based muscle extractor. Scans the whole title for muscle aliases and returns the detailed `lift` plus the rolled-up `muscle_group`. |
| `heat_maps.py` | Builds per-lift (detailed `lift`, split on `;`) calendar heatmaps for the app. |
| `reparse.py` | Non-destructive full re-parse of the dataset. Writes backup, regenerated and diff files; never overwrites the live data (see How to run). |
| `muscle_groups.json` | Parser config: `muscles` (alias regexes per muscle), `rollup` (detailed → major group), `back_returning_context` (phrases where "back" means "returning"). |
| `manual_overrides.json` | Per-title manual `lift`/`muscle_group` overrides, keyed by whitespace-normalised title. Takes precedence over the keyword scan. |
| `lift_types.json` | **Orphaned** - not referenced by any current code (see TODOs). |
| `video_data_final.json` | The dataset. One record per video (schema below). Committed. |
| `requirements.txt` | Python dependencies. |
| `.github/workflows/api_scraper.yml` | Daily cron (06:00 UTC) + manual dispatch. Runs `api_scraper.py`, commits and pushes `video_data_final.json`. |
| `folder_structure.md` | Hand-written file tree (currently stale - see TODOs). |

## How to run

```powershell
# Set up
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the app locally (use the module form if `streamlit` is not on PATH)
python -m streamlit run main.py
# then open http://localhost:8501 and click "Analyse"

# Pull new videos manually (needs YT_API_KEY in the environment)
$env:YT_API_KEY = "<key>"; python api_scraper.py

# Re-parse the whole dataset with the current parser (non-destructive)
python reparse.py
# review reparse_diff.md, then promote if happy:
Copy-Item video_data_final.regenerated.json video_data_final.json
```

The daily ingestion needs no manual step - the GitHub Action runs `api_scraper.py` and pushes the updated data. The Streamlit app on Community Cloud auto-redeploys from `master` (reboot from the dashboard if it lags).

## Inputs

- **YouTube Data API** - upload list + titles for `UCAuk798iHprjTtwlClkFxMA`. Requires `YT_API_KEY`.
- `video_data_final.json` - existing dataset; `api_scraper.py` reads it to skip already-stored URLs.
- `cookies.txt` - referenced by `scrape.py` `get_date_for_video` for date lookups (not committed; see TODOs).

## Outputs

- `video_data_final.json` - one record per video, `indent=2`:

  ```json
  {
    "title": "Hams - Bulk Day 25",
    "video_url": "https://www.youtube.com/watch?v=...",
    "upload_date": "24-05-2026",
    "event": "The Bulk Awakens",
    "day": "25",
    "lift": "Hamstrings",
    "muscle_group": "Legs"
  }
  ```

  - `lift` - detailed `;`-joined muscles (e.g. `Chest;Side Delts`), or `None`.
  - `muscle_group` - major-group rollup (`Arms`, `Back`, `Chest`, `Legs`, `Shoulders`, `Core`, `Cardio`), or `None`. The app's pie charts key off this; `heat_maps.py` still uses detailed `lift`.
- `reparse.py` artifacts (gitignored): `video_data_final.backup.json`, `video_data_final.regenerated.json`, `reparse_diff.md`.

## Dependencies

- Python 3.11+ (CI pins 3.11; tested locally on 3.13).
- See `requirements.txt`: `streamlit`, `pandas`, `matplotlib`, `numpy`, `seaborn`, `yt-dlp`, `google-api-python-client`, `google-auth-httplib2`.
- Env / secrets: `YT_API_KEY` - YouTube Data API key (GitHub repo secret for the Action; local env var for manual runs).

## Status

- Last shipped: 2026-06-01 - Streamlit pie charts now key off the `muscle_group` rollup (two views: exact major-group combos, and per-group split) instead of the long tail of detailed `lift` combos; `main.py` JSON save aligned to `indent=2` to match `api_scraper.py`.
- TODO:
  - Remove orphaned `lift_types.json` (no code references it).
  - Update `folder_structure.md` (lists `lift_types.json`, omits `api_scraper.py`, `muscle_parser.py`, `muscle_groups.json`, `manual_overrides.json`, `reparse.py`).
  - Add a `LICENSE` file or drop the licence claim (README previously pointed at a non-existent file).
  - Document or remove `scrape.py`'s `cookies.txt` dependency (file is not in the repo).

## Handoff notes

- Two parser configs drive everything: add an alias to `muscle_groups.json` for a missed muscle/pun, or an entry to `manual_overrides.json` for a one-off title the keyword scan can't handle. The "Analyse" run flags new videos with no muscle detected.
- `api_scraper.py` only enriches and prepends *new* videos; it never re-parses existing records. To re-derive everything after a parser change, use `reparse.py` and promote the regenerated file.
- Keep both JSON writers at `indent=2` (`main.py` and `api_scraper.py`) so the daily Action produces small diffs rather than reindenting the whole file.
