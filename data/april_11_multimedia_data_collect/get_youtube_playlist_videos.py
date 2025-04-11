import os
import csv
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file (for API key)
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")  # Or replace with your key in code
# Example 49ers highlights playlist:
PLAYLIST_ID = "PLBB205pkCsyvZ6tjCh_m5s21D0eeYJ8Ly"

def get_youtube_videos(playlist_id=PLAYLIST_ID, output_csv='youtube_highlights.csv'):
    """
    Fetches videos from a YouTube playlist (title, video ID, published date, etc.)
    Writes output to CSV.
    """
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable not set or provided!")
    
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    video_data = []
    page_token = None

    while True:
        playlist_req = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token
        )
        playlist_res = playlist_req.execute()
        
        for item in playlist_res['items']:
            snippet = item['snippet']
            title = snippet['title']
            description = snippet['description']
            video_id = snippet['resourceId']['videoId']
            published_at = snippet['publishedAt']
            
            video_data.append({
                "video_id": video_id,
                "title": title,
                "description": description,
                "published_at": published_at,
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            })
        
        page_token = playlist_res.get('nextPageToken')
        if not page_token:
            break
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["video_id", "title", "description", "published_at", "video_url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_data)
    
    print(f"[INFO] YouTube playlist data saved to {output_csv}")

if __name__ == "__main__":
    get_youtube_videos()
