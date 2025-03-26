import json
import yt_dlp
from tqdm import tqdm

with open('main_data.json', 'r') as infile:
    video_data = json.load(infile)

def get_upload_date(url):
    """Fetches the upload date of a YouTube video using yt_dlp."""
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        result = ydl.extract_info(url, download=False)
        return result.get('upload_date', 'Unknown')

for video in tqdm(video_data, desc="Fetching upload dates"):
    video['upload_date'] = get_upload_date(video['url'])

with open('updated_video_data.json', 'w') as outfile:
    json.dump(video_data, outfile, indent=4)

print("Updated video data has been written to 'updated_video_data.json'")