# cron_scraper.py

from scrape import get_youtube_videos, get_date_for_video
from analyse import clean_and_enrich_json
import json

CHANNEL_URL = "https://www.youtube.com/channel/UCAuk798iHprjTtwlClkFxMA"
DATA_FILE = "video_data_final.json"
LIFTS_FILE = "lift_types.json"

# Load existing data
with open(DATA_FILE, "r") as f:
    data = json.load(f)

with open(LIFTS_FILE, "r") as f:
    standard_lifts_data = json.load(f)

unique_lifts_master = set(standard_lifts_data.values())

# Get and filter new videos
res = get_youtube_videos(CHANNEL_URL)
existing_urls = {d['video_url'] for d in data}

res_new = []
for r in res:
    if r['video_url'] not in existing_urls:
        print(f"New video found: {r['title']}")
        r['upload_date'] = get_date_for_video(r['video_url'])
        res_new.append(r)

if not res_new:
    print("No new videos found.")
else:
    res_new = clean_and_enrich_json(res_new)[::-1]
    for x in res_new:
        data.insert(0, x)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"{len(res_new)} new videos added.")

    # Warn about new lifts
    unique_lifts = {r['lift'] for r in res_new if r['lift'] not in unique_lifts_master}
    if unique_lifts:
        print("New non-standard lifts found:")
        for lift in unique_lifts:
            print(f"- {lift}")
