import json
import yt_dlp as youtube_dl
import yt_dlp
from datetime import datetime

def get_youtube_videos(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        
        if 'entries' in result:
            videos = []
            for entry in result['entries']:
                video_data = {
                    'title': entry.get('title', 'No Title'),
                    'video_url': entry.get('url', ''),
                }
                videos.append(video_data)
            return videos
        else:
            return [{"error": "Failed to retrieve videos from this URL."}]

def get_date_for_video(video_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL({'cookiefile': 'auth/cookies.txt'}) as ydl:
        result = ydl.extract_info(video_url, download=False)
        raw_date = result.get('upload_date', '')

        if raw_date:
            try:
                formatted_date = datetime.strptime(raw_date, '%Y%m%d').strftime('%d-%m-%Y')
            except ValueError:
                formatted_date = raw_date
        else:
            formatted_date = ''
        
        return formatted_date

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/channel/UCAuk798iHprjTtwlClkFxMA"