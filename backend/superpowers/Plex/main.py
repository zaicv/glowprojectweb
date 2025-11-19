import httpx
import subprocess
import xml.etree.ElementTree as ET

PLEX_TOKEN = "_T2i8yEtx18sGVMsqHmR"
PLEX_BASE_URL = "https://100.83.147.76:32400"
HEADERS = {"X-Plex-Token": PLEX_TOKEN}


# ----------------------------
# Utility functions
# ----------------------------
def get_disk_usage(path):
    try:
        usage = subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')
        return usage
    except Exception:
        return "Unknown"

def get_video_quality(video):
    height = int(video.attrib.get("height", 0))
    if height >= 1080:
        return "HD (1080p)"
    elif height >= 720:
        return "HD (720p)"
    elif height > 0:
        return "SD"
    return "Unknown"

def get_media_duration(media_item):
    duration = media_item.attrib.get("duration", "0")
    if duration and duration != "0":
        try:
            # Convert milliseconds to minutes
            minutes = int(duration) // 60000
            hours = minutes // 60
            minutes = minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    return "Unknown"

def get_media_year(media_item):
    year = media_item.attrib.get("year", "")
    return year if year else "Unknown"

def get_media_rating(media_item):
    rating = media_item.attrib.get("rating", "")
    return rating if rating else "Unknown"


# ----------------------------
# Plex API functions (updated to accept **kwargs)
# ----------------------------
async def fetch_libraries(**kwargs):
    try:
        print(f"🔌 Fetching libraries from {PLEX_BASE_URL}/library/sections")
        print(f"🔑 Using headers: {HEADERS}")
        
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            res = await client.get(f"{PLEX_BASE_URL}/library/sections", headers=HEADERS)
            
            print(f"📡 Response status: {res.status_code}")
            print(f"📡 Response headers: {dict(res.headers)}")
            print(f"📡 Response text (first 500 chars): {res.text[:500]}")
            
            if res.status_code != 200:
                return {"error": f"Plex server returned {res.status_code}: {res.text}"}
            
            if not res.text.strip():
                return {"error": "Empty response from Plex server"}
            
            try:
                root = ET.fromstring(res.text)
                print(f"📄 XML root tag: {root.tag}")
                print(f"📄 XML root attribs: {root.attrib}")
                
                libraries = []
                directories = root.findall("Directory")
                print(f"📁 Found {len(directories)} Directory elements")
                
                for i, section in enumerate(directories):
                    print(f"📁 Processing directory {i}: {section.attrib}")
                    
                    title = section.attrib.get("title")
                    key = section.attrib.get("key")
                    library_type = section.attrib.get("type", "unknown")
                    
                    # Handle location safely
                    location_elem = section.find("Location")
                    if location_elem is not None:
                        location = location_elem.attrib.get("path", "")
                    else:
                        location = "Unknown"
                        print(f"⚠️ No Location element found for library {title}")
                    
                    # Get disk usage (skip if location is unknown)
                    if location != "Unknown":
                        disk_usage = get_disk_usage(location)
                    else:
                        disk_usage = "Unknown"
                    
                    libraries.append({
                        "title": title,
                        "key": key,
                        "type": library_type,
                        "location": location,
                        "disk_usage": disk_usage
                    })
                    
                    print(f"✅ Added library: {title} (key: {key}, type: {library_type})")

                print(f"📚 Total libraries found: {len(libraries)}")
                return {"libraries": libraries}
                
            except ET.ParseError as e:
                print(f"❌ XML Parse error: {e}")
                print(f"❌ Response text: {res.text}")
                return {"error": f"Failed to parse XML response: {e}"}
                
    except httpx.TimeoutException:
        print("❌ Timeout connecting to Plex server")
        return {"error": "Timeout connecting to Plex server"}
    except httpx.ConnectError as e:
        print(f"❌ Connection error: {e}")
        return {"error": f"Cannot connect to Plex server: {e}"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"error": f"Unexpected error: {e}"}


async def fetch_library_items(**kwargs):
    key = kwargs.get("key")
    if not key:
        return {"error": "Missing library key"}

    try:
        print(f"🎬 Fetching items from library {key}")
        
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            # Get all items
            all_url = f"{PLEX_BASE_URL}/library/sections/{key}/all"
            all_res = await client.get(all_url, headers=HEADERS)
            
            print(f"📡 All items response status: {all_res.status_code}")
            print(f"📡 All items response text (first 300 chars): {all_res.text[:300]}")
            
            if all_res.status_code != 200:
                return {"error": f"Plex server returned {all_res.status_code}: {all_res.text}"}
            
            root = ET.fromstring(all_res.text)
            items = []

            # Get ALL child elements regardless of type
            all_elements = list(root)
            print(f"🔍 Found {len(all_elements)} total XML elements")
            
            # Log what types of elements we found
            element_types = {}
            for elem in all_elements:
                elem_type = elem.tag
                if elem_type not in element_types:
                    element_types[elem_type] = 0
                element_types[elem_type] += 1
            
            print(f"📊 Element types found: {element_types}")

            for media_item in all_elements:
                title = media_item.attrib.get("title", "Unknown")
                thumb = media_item.attrib.get("thumb", "")
                rating_key = media_item.attrib.get("ratingKey", "")
                year = get_media_year(media_item)
                duration = get_media_duration(media_item)
                rating = get_media_rating(media_item)
                media_type = media_item.tag.lower()
                
                # Get added date for sorting
                added_at = media_item.attrib.get("addedAt", "0")
                
                # Get file size and quality for videos
                size_gb = "Unknown"
                quality = "Unknown"
                
                if media_type == "video":
                    part = media_item.find(".//Part")
                    if part is not None:
                        size_bytes = int(part.attrib.get("size", 0))
                        size_gb = f"{size_bytes / (1024 ** 3):.2f} GB" if size_bytes else "Unknown"
                    quality = get_video_quality(media_item)
                elif media_type == "track":
                    # For music tracks, get artist and album info
                    artist = media_item.attrib.get("grandparentTitle", "")
                    album = media_item.attrib.get("parentTitle", "")
                    if artist:
                        title = f"{artist} - {title}"
                elif media_type == "episode":
                    # For podcast episodes, get show name
                    show = media_item.attrib.get("grandparentTitle", "")
                    if show:
                        title = f"{show} - {title}"
                elif media_type == "artist":
                    # For artists, we might want to show track count
                    track_count = media_item.attrib.get("leafCount", "")
                    if track_count:
                        title = f"{title} ({track_count} tracks)"
                elif media_type == "album":
                    # For albums, show artist and track count
                    artist = media_item.attrib.get("parentTitle", "")
                    track_count = media_item.attrib.get("leafCount", "")
                    if artist:
                        title = f"{artist} - {title}"
                    if track_count:
                        title = f"{title} ({track_count} tracks)"
                
                items.append({
                    "title": title,
                    "thumb": thumb,
                    "rating_key": rating_key,
                    "year": year,
                    "duration": duration,
                    "rating": rating,
                    "size": size_gb,
                    "quality": quality,
                    "addedAt": added_at,
                    "type": media_type
                })

            # Sort by added date (most recent first)
            items.sort(key=lambda x: int(x.get("addedAt", "0")), reverse=True)
            
            print(f"🎬 Found {len(items)} items in library {key}")
            print(f"📊 Items by type: {dict((t, len([i for i in items if i['type'] == t])) for t in set(i['type'] for i in items))}")
            
            return {"items": items}
            
    except Exception as e:
        print(f"❌ Error fetching library items: {e}")
        return {"error": f"Error fetching library items: {e}"}


async def trigger_scan(**kwargs):
    key = kwargs.get("key")

    try:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            if key:
                url = f"{PLEX_BASE_URL}/library/sections/{key}/refresh"
                print(f"🔄 Triggering scan for library {key}: {url}")
                await client.get(url, headers=HEADERS)
                return {"message": f"✅ Scan triggered for library {key}"}
            else:
                # refresh ALL libraries if key not given
                url = f"{PLEX_BASE_URL}/library/sections/all/refresh"
                print(f"🔄 Triggering scan for all libraries: {url}")
                await client.get(url, headers=HEADERS)
                return {"message": "✅ Scan triggered for all libraries"}
                
    except Exception as e:
        print(f"❌ Error triggering scan: {e}")
        return {"error": f"Error triggering scan: {e}"}


# ----------------------------
# Superpower Wrapper
# ----------------------------
class Superpower:
    name = "plex"
    
    # Define what this superpower can handle
    intent_map = {
        "scan_plex": "Scan and refresh Plex libraries",
        "list_plex_libraries": "List all available Plex libraries",
        "list_plex_items": "List items in a specific Plex library",
        "play_video": "Play a video from Plex library",
        "stream_media": "Stream media content from Plex",
    }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        print(f"🎯 Plex superpower called with intent: {intent}, kwargs: {kwargs}")
        
        if intent == "scan_plex":
            return await trigger_scan(**kwargs)
        elif intent == "list_plex_libraries":
            return await fetch_libraries(**kwargs)
        elif intent == "list_plex_items":
            return await fetch_library_items(**kwargs)
        elif intent == "play_video":
            return await self.play_video(**kwargs)
        elif intent == "stream_media":
            return await self.play_video(**kwargs)  # Alias for play_video
        else:
            return {"error": f"Unknown Plex intent: {intent}"}

    async def play_video(self, title: str = None, library: str = None, **kwargs):
        """Get video playback information for Plex"""
        try:
            if not title:
                return "❌ Please provide a video title to play"
            
            # Search for the video in Plex
            video_info = await self.search_plex_video(title, library)
            
            if not video_info:
                return f"❌ Video '{title}' not found in Plex library"
            
            # Return structured data that the frontend can use to render the video player
            return {
                "type": "plex_video",
                "title": video_info.get("title", title),
                "videoSrc": video_info.get("streamUrl"),  # Direct stream URL or Plex web URL
                "thumbnailSrc": video_info.get("thumb"),
                "thumbnailAlt": f"Thumbnail for {video_info.get('title', title)}",
                "plexWebUrl": video_info.get("plexWebUrl"),  # Fallback Plex web interface URL
                "duration": video_info.get("duration"),
                "library": video_info.get("library"),
                "message": f"🎬 Ready to play: {video_info.get('title', title)}"
            }
            
        except Exception as e:
            return f"❌ Error playing video: {str(e)}"

    async def search_plex_video(self, title: str, library: str = None):
        """Search for a video in Plex and return streaming info"""
        try:
            # Get all libraries first
            libraries_data = await fetch_libraries()
            if "error" in libraries_data:
                return None
            
            # Search through libraries for the video
            for lib in libraries_data.get("libraries", []):
                try:
                    items_data = await fetch_library_items(key=lib["key"])
                    if "error" in items_data:
                        continue
                    
                    # Search for matching title
                    for item in items_data.get("items", []):
                        if title.lower() in item["title"].lower():
                            # Found a match! Now build the video info
                            rating_key = item["rating_key"]
                            
                            # Build Plex web URL (fallback option)
                            plex_web_url = f"https://app.plex.tv/desktop/#!/media/{rating_key}"
                            
                            # Build DIRECT STREAM URL using your Plex server and token
                            # This should work for direct streaming since you're authenticated
                            direct_stream_url = f"http://100.83.147.76:32400/library/metadata/{rating_key}/stream?X-Plex-Token={PLEX_TOKEN}"
                            
                            # Alternative: Use the media endpoint for better compatibility
                            media_url = f"http://100.83.147.76:32400/library/metadata/{rating_key}/media?X-Plex-Token={PLEX_TOKEN}"
                            
                            return {
                                "title": item["title"],
                                "streamUrl": direct_stream_url,  # Direct stream URL with your token
                                "plexWebUrl": plex_web_url,
                                "duration": None,
                                "thumb": item["thumb"],
                                "library": lib["title"]
                            }
                            
                except Exception as e:
                    print(f"Error searching library {lib['title']}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error searching Plex: {e}")
            return None