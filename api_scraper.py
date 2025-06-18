import os, json, datetime as dt
from googleapiclient.discovery import build

API_KEY      = os.environ["YT_API_KEY"]       # <-- set in GitHub Secrets
CHANNEL_ID   = "UCAuk798iHprjTtwlClkFxMA"     # Sam Sulek
OUTFILE      = "video_data_final.json"
ISO_FMT_OUT  = "%d-%m-%Y"                     # keep old dd-mm-yyyy format

youtube = build("youtube", "v3", developerKey=API_KEY, cache_discovery=False)

def uploads_playlist_id(channel_id: str) -> str:
    """Fetch the hidden ‘uploads’ playlist that holds every public video."""
    res = youtube.channels().list(
        part="contentDetails", id=channel_id, maxResults=1).execute()
    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def list_uploads(playlist_id: str):
    """Yield videoIds from the uploads playlist, 50 at a time (1 unit/call)"""
    token = None
    while True:
        res = youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id,
            maxResults=50, pageToken=token).execute()  # 1-unit :contentReference[oaicite:0]{index=0}
        for item in res["items"]:
            yield item["contentDetails"]["videoId"]
        token = res.get("nextPageToken")
        if not token:
            break

def fetch_metadata(video_ids):
    """Call videos.list for up to 50 IDs at once (1 unit/call)"""
    res = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=",".join(video_ids), maxResults=50).execute()  # 1-unit :contentReference[oaicite:1]{index=1}
    return res["items"]

def scrape_channel(channel_id: str):
    pl_id = uploads_playlist_id(channel_id)
    vids, batch = [], []

    for vid in list_uploads(pl_id):
        batch.append(vid)
        if len(batch) == 50:          # videos.list allows up to 50 IDs
            vids.extend(fetch_metadata(batch))
            batch.clear()
    if batch:
        vids.extend(fetch_metadata(batch))

    results = []
    for v in vids:
        s = v["snippet"]
        data = {
            "video_id":   v["id"],
            "video_url":  f"https://youtu.be/{v['id']}",
            "title":      s["title"],
            "upload_date": dt.datetime.fromisoformat(
                             s["publishedAt"].replace("Z", "+00:00")
                           ).strftime(ISO_FMT_OUT),
            "channel_id": s["channelId"],
            "channel_title": s["channelTitle"],
            "description": s["description"],
            # keep whatever extra fields you need:
            "views": v.get("statistics", {}).get("viewCount"),
            "duration": v["contentDetails"]["duration"],
        }
        results.append(data)
    return results

if __name__ == "__main__":
    videos = scrape_channel(CHANNEL_ID)
    with open(OUTFILE, "w", encoding="utf-8") as fh:
        json.dump(videos, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {len(videos)} records → {OUTFILE}")