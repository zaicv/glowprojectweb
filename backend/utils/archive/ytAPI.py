import os
import requests

YOUTUBE_API_KEY = "AIzaSyD15hAlt8C9V3tN53uIVDItKeGQJxPQrtg"

def search_youtube(query: str, max_results: int = 5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video"
    }

    response = requests.get(url, params=params)
    data = response.json()
    videos = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return videos