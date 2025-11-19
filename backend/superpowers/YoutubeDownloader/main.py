import os
import asyncio
import threading
import queue
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from yt_dlp import YoutubeDL
import json


# Configuration
DEFAULT_OUTPUT_DIR = "/Users/zai/Desktop/plex/Podcasts"

# Global progress and status tracking
progress_dict = {}
download_log = []


# ----------------------------
# Utility functions
# ----------------------------
def get_disk_usage(path):
    """Get disk usage statistics"""
    import shutil
    
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "total": f"{total // (1024**3)} GB",
            "used": f"{used // (1024**3)} GB", 
            "free": f"{free // (1024**3)} GB",
            "usage_percent": round((used / total) * 100, 1)
        }
    except Exception as e:
        return {"error": f"Could not get disk usage: {e}"}


def get_video_formats(url: str):
    """Get available formats for a video"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Process formats to get key info
            processed_formats = []
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':  # Video + Audio
                    processed_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'quality': fmt.get('format_note', 'Unknown'),
                        'filesize': fmt.get('filesize'),
                        'type': 'video+audio'
                    })
                elif fmt.get('vcodec') != 'none':  # Video only
                    processed_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'quality': fmt.get('format_note', 'Unknown'),
                        'filesize': fmt.get('filesize'),
                        'type': 'video'
                    })
                elif fmt.get('acodec') != 'none':  # Audio only
                    processed_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'quality': fmt.get('format_note', 'Unknown'),
                        'filesize': fmt.get('filesize'),
                        'type': 'audio'
                    })
            
            return {
                "title": info.get('title'),
                "uploader": info.get('uploader'),
                "duration": info.get('duration'),
                "formats": processed_formats[:20]  # Limit to first 20 formats
            }
    except Exception as e:
        return {"error": f"Could not get formats: {e}"}


def progress_hook(d):
    """Standard progress hook for yt-dlp"""
    info = d.get('info_dict', {})
    video_id = info.get('id', 'unknown')

    if video_id not in progress_dict:
        progress_dict[video_id] = {}

    # Update progress data
    downloaded = d.get('downloaded_bytes', 0)
    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
    speed = d.get('speed', 0)
    eta = d.get('eta', 0)

    progress_dict[video_id] = {
        'status': d.get('status', 'unknown'),
        'downloaded': downloaded,
        'total': total,
        'progress': (downloaded / total * 100) if total > 0 else 0,
        'speed': speed,
        'eta': eta,
        'filename': d.get('filename', ''),
        'last_update': datetime.now().isoformat()
    }


# ----------------------------
# Async WebSocket Progress Handler
# ----------------------------
async def progress_monitor(progress_queue: queue.Queue, websocket_callback: Callable, stop_event: threading.Event):
    """Monitor progress queue and send WebSocket updates"""
    while not stop_event.is_set():
        try:
            # Check for progress updates (non-blocking)
            try:
                progress_data = progress_queue.get_nowait()
                await websocket_callback(progress_data)
            except queue.Empty:
                pass
            
            # Small delay to prevent excessive CPU usage
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Progress monitor error: {e}")
            break


async def download_video(url: str, format: str = "mp4", quality: str = None, 
                        output_dir: str = None, custom_filename: str = None,
                        websocket_callback: Optional[Callable] = None, **kwargs):
    """
    Download video with real-time WebSocket progress updates
    """
    try:
        print(f"🔍 Starting download: {url}")
        
        download_path = output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(download_path, exist_ok=True)

        # Handle custom filename
        if custom_filename:
            if format == "mp3":
                output_template = f'%(title)s {custom_filename}.%(ext)s'
            else:
                output_template = f'%(title)s {custom_filename}.%(ext)s'
        else:
            output_template = '%(title)s.%(ext)s'

        # First, get video info to check available formats
        if websocket_callback:
            await websocket_callback({
                "progress": 0,
                "status": "checking_formats",
                "message": "Checking available formats..."
            })

        # Get video info to validate format availability
        video_info = await get_video_info(url=url)
        if video_info.get("error"):
            if websocket_callback:
                await websocket_callback({
                    "progress": 0,
                    "status": "error",
                    "message": f"Could not get video info: {video_info['error']}"
                })
            return {"error": f"Could not get video info: {video_info['error']}", "success": False}

        # Determine format and quality with fallbacks
        if format == "mp3":
            format_selector = 'bestaudio/best'
        else:
            # Try the requested quality first, then fallback to lower qualities
            quality_fallbacks = []
            if quality:
                quality_map = {
                    "2160": ["best[height<=2160]", "best[height<=1440]", "best[height<=1080]", "best[height<=720]", "best"],
                    "1440": ["best[height<=1440]", "best[height<=1080]", "best[height<=720]", "best"],
                    "1080": ["best[height<=1080]", "best[height<=720]", "best[height<=480]", "best"],
                    "720": ["best[height<=720]", "best[height<=480]", "best"],
                    "480": ["best[height<=480]", "best"]
                }
                quality_fallbacks = quality_map.get(quality, ["best[height<=1080]", "best[height<=720]", "best"])
            else:
                quality_fallbacks = ["best[height<=1080]", "best[height<=720]", "best"]
            
            format_selector = quality_fallbacks[0]  # Start with the first (best) option

        # Create progress queue and stop event for thread communication
        progress_queue = queue.Queue() if websocket_callback else None
        stop_event = threading.Event() if websocket_callback else None
        monitor_task = None

        # Start progress monitor if we have a WebSocket callback
        if websocket_callback:
            monitor_task = asyncio.create_task(
                progress_monitor(progress_queue, websocket_callback, stop_event)
            )

        # Create progress hook that puts updates in queue
        def threaded_progress_hook(d):
            try:
                if d['status'] == 'downloading' and progress_queue:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    
                    if total > 0:
                        progress_percentage = (downloaded / total) * 100
                        
                        # Put progress data in queue (non-blocking)
                        try:
                            progress_queue.put_nowait({
                                "progress": round(progress_percentage, 1),
                                "downloaded": downloaded,
                                "total": total,
                                "eta": eta or 0,
                                "speed": speed or 0,
                                "status": "downloading",
                                "message": f"Downloading... {progress_percentage:.1f}%"
                            })
                        except queue.Full:
                            pass  # Skip update if queue is full
                        
                elif d['status'] == 'finished' and progress_queue:
                    try:
                        progress_queue.put_nowait({
                            "progress": 100,
                            "status": "processing",
                            "message": "Processing download..."
                        })
                    except queue.Full:
                        pass
                        
            except Exception as e:
                print(f"Progress hook error: {e}")

        # Try multiple format selectors with fallback
        download_success = False
        last_error = None
        used_format = None
        
        # For video downloads, try different quality fallbacks
        if format != "mp3":
            format_attempts = quality_fallbacks
        else:
            format_attempts = [format_selector]

        for attempt, current_format in enumerate(format_attempts):
            try:
                if websocket_callback:
                    await websocket_callback({
                        "progress": 0,
                        "status": "trying_format",
                        "message": f"Trying format: {current_format} (attempt {attempt + 1}/{len(format_attempts)})"
                    })

                # Enhanced yt-dlp options
                ydl_opts = {
                    'format': current_format,
                    'outtmpl': os.path.join(download_path, output_template),
                    'progress_hooks': [threaded_progress_hook] if websocket_callback else [progress_hook],
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'ignoreerrors': False,
                    'no_warnings': False,
                    'extractaudio': format == "mp3",
                    'audioformat': 'mp3' if format == "mp3" else None,
                    'audioquality': kwargs.get('audio_quality', '192') if format == "mp3" else None,
                    
                    # Enhanced headers and options to avoid 403
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                    },
                    'extractor_args': {
                        'youtube': {
                            'skip': ['hls', 'dash'],
                            'player_client': ['android', 'web'],
                        }
                    },
                    'retries': 3,
                    'fragment_retries': 3,
                    'retry_sleep_functions': {'http': lambda n: 2**n},
                }

                # Send initial status
                if websocket_callback:
                    await websocket_callback({
                        "progress": 0,
                        "status": "initializing",
                        "message": "Starting download..."
                    })

                with YoutubeDL(ydl_opts) as ydl:
                    # Get video info first
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    
                    # Send starting message
                    if websocket_callback:
                        await websocket_callback({
                            "progress": 0,
                            "status": "starting",
                            "message": f"Starting download of: {title}"
                        })
                    
                    # Download the video in a separate thread to not block the event loop
                    def download_thread():
                        ydl.download([url])
                    
                    # Run download in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, download_thread)
                    
                    # If we get here, download was successful
                    download_success = True
                    used_format = current_format
                    break
                    
            except Exception as e:
                last_error = str(e)
                print(f"❌ Format {current_format} failed: {e}")
                
                # Check for specific format availability error
                if "Requested format is not available" in str(e):
                    print(f"⚠️ Format {current_format} not available for this video, trying fallback...")
                    if websocket_callback:
                        await websocket_callback({
                            "progress": 0,
                            "status": "format_unavailable",
                            "message": f"Format {current_format} not available, trying lower quality..."
                        })
                else:
                    print(f"❌ Unexpected error with format {current_format}: {e}")
                
                # If this is the last attempt, we'll fail
                if attempt == len(format_attempts) - 1:
                    break
                    
                # Otherwise, try the next format
                if websocket_callback:
                    await websocket_callback({
                        "progress": 0,
                        "status": "retrying",
                        "message": f"Format {current_format} failed, trying next option..."
                    })
                continue

        if not download_success:
            error_msg = f"All format attempts failed. Last error: {last_error}"
            if websocket_callback:
                await websocket_callback({
                    "progress": 0,
                    "status": "error",
                    "message": error_msg
                })
            return {"error": error_msg, "success": False}

        # Get the actual filename that was created (re-extract info for the successful format)
        try:
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
        except:
            # Fallback filename generation
            filename = os.path.join(download_path, f"{title}.{format}")
        
        # For MP3, update the extension
        if format == "mp3":
            base_name = os.path.splitext(filename)[0]
            filename = base_name + '.mp3'
        
        # Apply custom filename if provided
        if custom_filename and os.path.exists(filename):
            directory = os.path.dirname(filename)
            original_name = os.path.splitext(os.path.basename(filename))[0]
            extension = os.path.splitext(filename)[1]
            
            # Create new filename with custom suffix
            new_filename = os.path.join(directory, f"{original_name} {custom_filename}{extension}")
            
            # Rename the file
            try:
                os.rename(filename, new_filename)
                filename = new_filename
                print(f"✅ Renamed file to: {os.path.basename(filename)}")
            except Exception as e:
                print(f"⚠️ Could not rename file: {e}")
        
        # Send completion message
        if websocket_callback:
            await websocket_callback({
                "progress": 100,
                "status": "complete",
                "downloaded": os.path.getsize(filename) if os.path.exists(filename) else 0,
                "total": os.path.getsize(filename) if os.path.exists(filename) else 0,
                "eta": 0,
                "filename": os.path.basename(filename),
                "download_url": f"/downloads/{os.path.basename(filename)}",
                "title": title,
                "message": f"Download complete! Used format: {used_format}"
            })

        # Log successful download
        download_log.append({
            "url": url,
            "title": title,
            "format": format,
            "quality": quality,
            "filename": os.path.basename(filename),
            "download_time": datetime.now().isoformat(),
            "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0
        })

        return {
            "success": True,
            "title": title,
            "filename": os.path.basename(filename),
            "download_url": f"/downloads/{os.path.basename(filename)}",
            "format": format,
            "quality": quality,
            "duration": duration,
            "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
            "used_format": used_format
        }

    except Exception as e:
        if websocket_callback:
            await websocket_callback({
                "progress": 0,
                "status": "error",
                "message": f"Download failed: {str(e)}"
            })
        
        print(f"❌ Download error: {e}")
        return {"error": f"Download failed: {e}", "success": False}
    
    finally:
        # Clean up progress monitor
        if stop_event:
            stop_event.set()
        if monitor_task:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass


def get_video_quality_info(info: Dict) -> Dict:
    """Extract quality information from video info"""
    try:
        quality_info = {
            "best_video": "Unknown",
            "best_audio": "Unknown", 
            "available_qualities": []
        }
        
        formats = info.get('formats', [])
        if not formats:
            return quality_info
        
        # Find best video quality
        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
        if video_formats:
            best_video = max(video_formats, key=lambda x: x.get('height', 0))
            quality_info["best_video"] = f"{best_video.get('height', 0)}p"
        
        # Find best audio quality
        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('abr')]
        if audio_formats:
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
            quality_info["best_audio"] = f"{best_audio.get('abr', 0)}kbps"
        
        # Get available video qualities
        unique_heights = set()
        for f in video_formats:
            height = f.get('height')
            if height:
                unique_heights.add(height)
        
        quality_info["available_qualities"] = sorted(list(unique_heights), reverse=True)
        
        return quality_info
        
    except Exception as e:
        print(f"❌ Error extracting quality info: {e}")
        return {
            "best_video": "Unknown",
            "best_audio": "Unknown",
            "available_qualities": []
        }


async def get_video_info(**kwargs):
    """Get video information without downloading"""
    url = kwargs.get("url")
    if not url:
        return {"error": "URL is required"}

    try:
        print(f"🔍 Getting video info: {url}")
        
        # Try multiple extraction methods with different options
        extraction_methods = [
            # Method 1: Standard extraction
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            },
            # Method 2: Flat extraction (less detailed but more reliable)
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
            },
            # Method 3: Minimal extraction with different extractor args
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "extractor_args": {
                    "youtube": {
                        "skip": ["hls", "dash"],
                        "player_client": ["android", "web"],
                    }
                }
            },
            # Method 4: Even more minimal
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "ignoreerrors": True,
            },
            # Method 5: Ultra-minimal with different user agent
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "ignoreerrors": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                }
            }
        ]
        
        # Add cookies if available
        cookie_file = "/Users/zai/The GlowOS/Superpowers FastAPI Apps/Youtube Downloader/working yt/cookies.txt"
        
        last_error = None
        for i, opts in enumerate(extraction_methods):
            try:
                print(f"🔍 Trying extraction method {i + 1}/{len(extraction_methods)}")
                
                if os.path.exists(cookie_file):
                    opts["cookiefile"] = cookie_file
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, _extract_info, opts, url)
                
                if result.get("success"):
                    info = result["info"]
                    print(f"✅ Successfully extracted info with method {i + 1}")
                    
                    # Format duration
                    duration = info.get("duration")
                    duration_str = None
                    if duration:
                        hours = duration // 3600
                        minutes = (duration % 3600) // 60
                        seconds = duration % 60
                        if hours:
                            duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                        else:
                            duration_str = f"{minutes}:{seconds:02d}"
                    
                    # Get file size estimate
                    filesize = info.get("filesize") or info.get("filesize_approx", 0)
                    file_size = f"{filesize / (1024**3):.2f} GB" if filesize else "Unknown"
                    
                    return {
                        "title": info.get("title"),
                        "uploader": info.get("uploader"),
                        "upload_date": info.get("upload_date"),
                        "duration": duration_str,
                        "view_count": info.get("view_count"),
                        "like_count": info.get("like_count"),
                        "description": (info.get("description", "")[:200] + "...") if info.get("description") else "",
                        "thumbnail": info.get("thumbnail"),
                        "quality": get_video_quality_info(info),
                        "file_size_estimate": file_size,
                        "extractor": info.get("extractor"),
                        "webpage_url": info.get("webpage_url", url),
                        "extraction_method": f"method_{i + 1}"
                    }
                else:
                    last_error = result.get("error", "Unknown error")
                    print(f"❌ Method {i + 1} failed: {last_error}")
                    continue
                    
            except Exception as e:
                last_error = str(e)
                print(f"❌ Method {i + 1} exception: {e}")
                continue
        
        # If all methods failed
        return {"error": f"All extraction methods failed. Last error: {last_error}"}
            
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return {"error": f"Failed to get video info: {e}"}


def _extract_info(opts: Dict, url: str) -> Dict:
    """Extract video information synchronously"""
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {"success": True, "info": info}
    except Exception as e:
        error_msg = str(e)
        # Log specific error types for debugging
        if "Requested format is not available" in error_msg:
            print(f"⚠️ Format availability error: {error_msg}")
        elif "Video unavailable" in error_msg:
            print(f"⚠️ Video unavailable: {error_msg}")
        elif "Private video" in error_msg:
            print(f"⚠️ Private video: {error_msg}")
        else:
            print(f"⚠️ Extraction error: {error_msg}")
        return {"success": False, "error": error_msg}


async def get_download_history(**kwargs):
    """Get download history"""
    limit = kwargs.get("limit", 50)
    
    try:
        recent_downloads = download_log[-limit:] if limit else download_log
        
        return {
            "downloads": recent_downloads,
            "total": len(download_log),
            "message": f"Found {len(download_log)} downloads in history"
        }
        
    except Exception as e:
        print(f"❌ Error getting download history: {e}")
        return {"error": f"Error getting download history: {e}"}


async def clear_download_history(**kwargs):
    """Clear download history"""
    try:
        global download_log
        count = len(download_log)
        download_log.clear()
        return {"message": f"✅ Cleared {count} downloads from history"}
        
    except Exception as e:
        print(f"❌ Error clearing download history: {e}")
        return {"error": f"Error clearing download history: {e}"}


async def get_download_progress(**kwargs):
    """Get download progress for a video"""
    video_id = kwargs.get("video_id")
    
    try:
        if video_id and video_id in progress_dict:
            progress = progress_dict[video_id]
            
            # Calculate percentage if we have the data
            if progress.get('total_bytes') and progress.get('downloaded_bytes'):
                percentage = (progress['downloaded_bytes'] / progress['total_bytes']) * 100
                progress['percentage'] = round(percentage, 2)
            
            return {"progress": progress}
        
        # Return all progress if no specific video_id
        if not video_id and progress_dict:
            return {"all_progress": progress_dict}
        
        return {"progress": None, "message": "No progress data found"}
        
    except Exception as e:
        print(f"❌ Error getting download progress: {e}")
        return {"error": f"Error getting download progress: {e}"}


async def get_output_directory_info(**kwargs):
    """Get information about the output directory"""
    output_dir = kwargs.get("output_dir", DEFAULT_OUTPUT_DIR)
    
    try:
        if not os.path.exists(output_dir):
            return {"error": f"Directory does not exist: {output_dir}"}
        
        # Get directory size
        disk_usage = get_disk_usage(output_dir)
        
        # Count files
        file_count = 0
        video_files = []
        
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.m4a', '.wav')):
                    file_count += 1
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    video_files.append({
                        "name": file,
                        "size": f"{file_size / (1024**2):.1f} MB",
                        "path": file_path
                    })
        
        return {
            "output_dir": output_dir,
            "disk_usage": disk_usage,
            "file_count": file_count,
            "recent_files": video_files[-10:],  # Last 10 files
            "total_files": len(video_files)
        }
        
    except Exception as e:
        print(f"❌ Error getting directory info: {e}")
        return {"error": f"Error getting directory info: {e}"}


# ----------------------------
# Superpower Wrapper
# ----------------------------
class Superpower:
    name = "youtube"
    description = "Download videos and audio from YouTube and other platforms using yt-dlp"
    
    # Define what this superpower can handle
    intent_map = {
        "download_video": "Download a video from YouTube or other platforms",
        "download_audio": "Download audio-only from YouTube or other platforms",
        "get_video_info": "Get information about a video without downloading",
        "download_progress": "Check download progress for videos",
        "download_history": "View download history",
        "clear_history": "Clear download history",
        "get_directory_info": "Get information about download directory",
        "download": "General download intent (alias for download_video)"
    }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        print(f"🎯 YouTube superpower called with intent: {intent}, kwargs: {kwargs}")
        
        try:
            if intent in ["download_video", "download"]:
                kwargs.setdefault("format", "mp4")
                # Handle fallback mode for problematic videos
                if kwargs.get("fallback_mode"):
                    kwargs.setdefault("quality", "720")  # Use lower quality for fallback
                return await download_video(**kwargs)  # kwargs now includes websocket_callback
                
            elif intent == "download_audio":
                kwargs.setdefault("format", "mp3")
                kwargs.setdefault("audio_quality", "192")
                return await download_video(**kwargs)  # kwargs now includes websocket_callback
                
            elif intent == "get_video_info":
                return await get_video_info(**kwargs)
                
            elif intent == "download_progress":
                return await get_download_progress(**kwargs)
                
            elif intent == "download_history":
                return await get_download_history(**kwargs)
                
            elif intent == "clear_history":
                return await clear_download_history(**kwargs)
                
            elif intent == "get_directory_info":
                return await get_output_directory_info(**kwargs)
                
            else:
                return {"error": f"Unknown YouTube intent: {intent}"}
                
        except Exception as e:
            print(f"❌ YouTube superpower error: {e}")
            return {"error": f"YouTube superpower error: {str(e)}"}