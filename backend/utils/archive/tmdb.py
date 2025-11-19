import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()  # ✅ Load .env before using os.getenv

TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # ✅ Now this will work

def extract_title_from_filename(filename: str) -> str:
    """
    Extract a searchable title from common MakeMKV output patterns
    """
    # Remove file extension
    name = os.path.splitext(filename)[0]
    
    # Pattern 1: "Show Season X Disc Y_tXX" -> "Show"
    season_disc_pattern = r'^(.+?)\s+Season\s+\d+\s+Disc\s+\d+.*$'
    match = re.match(season_disc_pattern, name, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: "Movie Title_tXX" -> "Movie Title"
    title_track_pattern = r'^(.+?)_t\d+$'
    match = re.match(title_track_pattern, name)
    if match:
        return match.group(1).strip()
    
    # Pattern 3: "title_tXX" -> likely a movie, try parent folder name
    if name.lower().startswith('title_'):
        return None  # Will need manual input
    
    # Pattern 4: Single letter patterns like "B1_t01" -> likely episodes, needs manual input
    if re.match(r'^[A-Z]\d+_t\d+$', name):
        return None
    
    # Pattern 5: Just return the name as-is for other cases
    return name

def fetch_tmdb_metadata(title: str):
    if not TMDB_API_KEY:
        print("❌ TMDB API Key is missing or not loaded.")
        return None

    # Try to extract a better title from the filename
    better_title = extract_title_from_filename(title)
    search_title = better_title if better_title else title
    
    # Don't search if we couldn't extract a meaningful title
    if not search_title or len(search_title.strip()) < 3:
        print(f"⚠️ Filename '{title}' doesn't contain a searchable title")
        return None

    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={search_title}"
    print(f"🌐 TMDB Request URL: {url}")
    try:
        res = requests.get(url, timeout=10)
        print(f"🔁 TMDB Status Code: {res.status_code}")
        print(f"📦 TMDB Raw JSON: {res.text[:500]}")  # only show first 500 chars

        if not res.ok:
            print("❌ TMDB request failed.")
            return None

        data = res.json()
        results = data.get("results", [])

        if not results:
            print(f"⚠️ No TMDB results for '{search_title}'.")
            return None

        item = results[0]
        extracted = {
            "title": item.get("title") or item.get("name"),
            "year": (item.get("release_date") or item.get("first_air_date") or "????")[:4],
            "type": "movie" if item["media_type"] == "movie" else "tv"
        }

        print(f"✅ TMDB Extracted Metadata: {extracted}")
        return extracted

    except Exception as e:
        print(f"❌ Exception while fetching TMDB metadata: {e}")
        return None