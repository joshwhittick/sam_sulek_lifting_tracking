import os
import json
import datetime as dt
from googleapiclient.discovery import build
from analyse import clean_and_enrich_json

# === CONFIGURATION ===
API_KEY = os.environ["YT_API_KEY"]
CHANNEL_ID = "UCAuk798iHprjTtwlClkFxMA"  # Sam Sulek
OUTFILE = "video_data_final.json"
ISO_FMT = "%d-%m-%Y"

# === YouTube API Setup ===
youtube = build("youtube", "v3", developerKey=API_KEY, cache_discovery=False)

def get_uploads_playlist_id(channel_id):
    res = youtube.channels().list(
        part="contentDetails", id=channel_id, maxResults=1
    ).execute()
    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def fetch_all_video_ids(playlist_id):
    video_ids = []
    token = None
    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=token
        ).execute()
        for item in res["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
        token = res.get("nextPageToken")
        if not token:
            break
    return video_ids

def fetch_video_metadata(video_ids):
    results = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        res = youtube.videos().list(
            part="snippet",
            id=",".join(batch_ids)
        ).execute()
        for item in res["items"]:
            snippet = item["snippet"]
            video_url = f"https://www.youtube.com/watch?v={item['id']}"
            upload_date = dt.datetime.strptime(
                snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime(ISO_FMT)
            results.append({
                "title": snippet["title"],
                "video_url": video_url,
                "upload_date": upload_date
            })
    return results

# === Load Existing Data ===
if os.path.exists(OUTFILE):
    with open(OUTFILE, "r") as f:
        existing_data = json.load(f)
else:
    existing_data = []

existing_urls = {entry["video_url"] for entry in existing_data}

# === Fetch New Videos from API ===
print("Fetching new videos...")
playlist_id = get_uploads_playlist_id(CHANNEL_ID)
all_video_ids = fetch_all_video_ids(playlist_id)
fetched_videos = fetch_video_metadata(all_video_ids)

# === Filter Out Already Stored Videos ===
new_videos = [v for v in fetched_videos if v["video_url"] not in existing_urls]

if not new_videos:
    print("No new videos found.")
else:
    print(f"{len(new_videos)} new videos found. Enriching...")
    enriched_videos = clean_and_enrich_json(new_videos)[::-1]  # latest last

    for video in enriched_videos:
        existing_data.insert(0, video)  # prepend new videos

    with open(OUTFILE, "w") as f:
        json.dump(existing_data, f, indent=2)

    print(f"{len(enriched_videos)} videos added and saved to {OUTFILE}.")