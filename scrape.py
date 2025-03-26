import json
from pytube import Channel
import youtube_dl
import yt_dlp as youtube_dl
import yt_dlp

def get_youtube_videos_v3(channel_url):
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
                    'url': entry.get('url', '')
                }
                videos.append(video_data)
            return json.dumps(videos, indent=4)
        else:
            return json.dumps({"error": "Failed to retrieve videos from this URL."}, indent=4)    

def get_youtube_videos(channel_url):
    channel = Channel(channel_url)
    videos = {}
    for video in channel.videos:
        videos[video.watch_url] = video.title
    
    video_dict = json.dumps(videos, indent=4)
    return video_dict

def get_youtube_videos_v2(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if 'entries' in result:
            videos = []
            for entry in result['entries']:
                video_data = {
                    'title': entry.get('title', 'No Title'),
                    'url': entry.get('url', '')
                }
                videos.append(video_data)
            return json.dumps(videos, indent=4)
        else:
            return json.dumps({"error": "Failed to retrieve videos from this URL."}, indent=4)

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/channel/UCAuk798iHprjTtwlClkFxMA"
    
    try:
        video_dict = get_youtube_videos(channel_url)
        print("pytube results:")
        print(video_dict)
        with open('video_dict.json', 'w') as f:
            f.write(video_dict)
    except Exception as e:
        print(f"Error: {e}")    
    
    try:
        video_dict_2 = get_youtube_videos_v2(channel_url)
        print("youtube_dl results:")
        print(video_dict_2)
        with open('video_dict_2.json', 'w') as f:
            f.write(video_dict_2)
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        video_dict_3 = get_youtube_videos_v3(channel_url)
        print("yt_dlp results:")
        print(video_dict_3)
        with open('video_dict_3.json', 'w') as f:
            f.write(video_dict_3)
    except Exception as e:
        print(f"yt_dlp Error: {e}")