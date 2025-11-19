import os
import subprocess
import shutil
import time
import asyncio
import platform
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List, Tuple
from utils.archive.tmdb import fetch_tmdb_metadata
from utils.archive.plex_namer import rename_to_plex_format

# Configuration
MOVIES_FOLDER = "/Users/zai/Movies"
PLEX_BASE = "/Users/zai/Desktop/plex"

# Global progress tracking and session storage
rip_progress = {}
pending_sessions = {}  # Store paused processing sessions


def get_folder_context_for_file(file_path: Path, base_path: Path) -> str:
    """
    Get the most relevant folder name for metadata inference
    Examples:
    - /Users/zai/Movies/The Flash Season 1 Disc 1/file.mkv -> "The Flash Season 1 Disc 1"
    - /Users/zai/Movies/Spy Kids 2/title_t01.mkv -> "Spy Kids 2"
    - /Users/zai/Movies/file.mkv -> None (direct in movies folder)
    """
    try:
        relative_path = file_path.relative_to(base_path)
        parts = relative_path.parts
        
        if len(parts) > 1:
            # File is in a subfolder, use the immediate parent folder name
            return parts[-2]  # -1 is the filename, -2 is the parent folder
        else:
            # File is directly in the movies folder
            return None
    except ValueError:
        # File is not within base_path
        return None


def create_pretty_filename_from_folder(folder_name: str, track_number: str = None, episode_number: str = None) -> str:
    """
    Create a pretty filename from folder name when TMDB fails
    Examples:
    - "The Flash Season 1 Disc 1" -> "The Flash S1E01", "The Flash S1E02", etc.
    - "DEXTER_SEASON_2_DISC_1" -> "Dexter Season 2E01", "Dexter Season 2E02", etc.
    - "Spy Kids 2" -> "Spy Kids 2" (movie)
    """
    if not folder_name:
        return "Unknown"
    
    # Clean up the folder name
    clean_name = folder_name.replace('_', ' ').replace('-', ' ')
    
    # Handle season patterns
    season_patterns = [
        (r'(.+?)\s+Season\s+(\d+)', r'\1 S\2'),  # "The Flash Season 1" -> "The Flash S1"
        (r'(.+?)\s+S(\d+)', r'\1 S\2'),  # "The Flash S1" -> "The Flash S1"
        (r'(.+?)\s+SEASON\s+(\d+)', r'\1 Season \2'),  # "DEXTER SEASON 2" -> "Dexter Season 2"
    ]
    
    for pattern, replacement in season_patterns:
        match = re.match(pattern, clean_name, re.IGNORECASE)
        if match:
            base_title = match.group(1).title()
            season_part = re.sub(pattern, replacement, clean_name, flags=re.IGNORECASE)
            
            # Use provided episode number or extract from track
            if episode_number:
                return f"{season_part}E{episode_number.zfill(2)}"
            elif track_number:
                # Extract episode number from track (e.g., "t01" -> "01")
                episode_match = re.search(r't(\d+)', track_number)
                if episode_match:
                    episode_num = episode_match.group(1)
                    return f"{season_part}E{episode_num}"
            
            return season_part
    
    # If no season pattern, treat as movie or general title
    pretty_title = clean_name.title()
    
    # Remove common disc indicators
    pretty_title = re.sub(r'\s+Disc\s+\d+', '', pretty_title, flags=re.IGNORECASE)
    
    return pretty_title


def detect_media_type_from_folder(folder_name: str) -> str:
    """
    Detect if this is likely a TV show or movie based on folder name
    """
    if not folder_name:
        return "movie"
    
    tv_indicators = ['season', 's1', 's2', 's3', 's4', 's5', 'disc', 'episode']
    folder_lower = folder_name.lower()
    
    for indicator in tv_indicators:
        if indicator in folder_lower:
            return "tv"
    
    return "movie"


def determine_plex_destination(title: str, media_type: str, folder_context: str = None) -> str:
    """
    Determine the best Plex library folder based on content analysis
    """
    if media_type == "movie":
        kids_keywords = ['vampirina', 'disney', 'kids', 'children', 'family', 'animated']
        title_lower = title.lower()
        folder_lower = (folder_context or "").lower()
        
        for keyword in kids_keywords:
            if keyword in title_lower or keyword in folder_lower:
                return "Kid's Movies"
        return "Movies"
    else:
        kids_tv_keywords = ['vampirina', 'disney', 'kids', 'children', 'family', 'animated']
        title_lower = title.lower()
        folder_lower = (folder_context or "").lower()
        
        for keyword in kids_tv_keywords:
            if keyword in title_lower or keyword in folder_lower:
                return "Kid's TV Shows"
        return "TV Shows"


def get_volume_name_from_drive_path(drive_path: str) -> str:
    """
    Extract volume name from drive path like /Volumes/THE_FLASH_S1
    """
    if not drive_path:
        return None
    
    if drive_path.startswith('/Volumes/'):
        return os.path.basename(drive_path)
    
    return None


def run_makemkv(volume_name: str = None):
    """Run MakeMKV to rip disc into volume-specific folder"""
    try:
        print("🔁 Starting MakeMKV disc ripping...")
        
        # Create destination folder based on volume name
        if volume_name:
            rip_destination = os.path.join(MOVIES_FOLDER, volume_name)
        else:
            rip_destination = MOVIES_FOLDER
        
        # Create the destination folder if it doesn't exist
        os.makedirs(rip_destination, exist_ok=True)
        print(f"📁 Ripping to: {rip_destination}")
        
        subprocess.run([
            "/Applications/MakeMKV.app/Contents/MacOS/makemkvcon",
            "mkv", "disc:0", "all", rip_destination
        ], check=True)
        return True, rip_destination
    except subprocess.CalledProcessError as e:
        print(f"❌ MakeMKV failed: {e}")
        return False, None


def get_ripped_files(specific_folder: str = None) -> List[Tuple[Path, str]]:
    """
    Get list of ripped video files with their folder context, optionally from a specific folder
    Returns: List of tuples (file_path, folder_context)
    """
    try:
        search_path = Path(specific_folder) if specific_folder else Path(MOVIES_FOLDER)
        
        if not search_path.exists():
            print(f"⚠️ Search path does not exist: {search_path}")
            return []
        
        print(f"🔍 Recursively scanning {search_path} for video files...")
        
        # Find all video files recursively
        video_files = []
        for file_path in search_path.rglob("*"):
            if file_path.suffix.lower() in [".mkv", ".mp4"] and file_path.is_file():
                folder_context = get_folder_context_for_file(file_path, search_path)
                video_files.append((file_path, folder_context))
        
        print(f"🎯 Found {len(video_files)} video file(s):")
        for file_path, folder_context in video_files:
            rel_path = file_path.relative_to(search_path)
            print(f"   - {rel_path} | Folder: {folder_context or 'Root'}")
        
        return video_files
        
    except Exception as e:
        print(f"❌ Failed to scan directory {search_path}: {e}")
        return []


async def get_pending_files(**kwargs):
    """Get list of files that need manual metadata"""
    try:
        ripped_files = get_ripped_files()
        pending_files = []
        
        # Only check metadata if explicitly requested
        check_metadata = kwargs.get("check_metadata", False)
        
        for file_path, folder_context in ripped_files:
            if check_metadata:
                # Try to get metadata automatically - this triggers TMDB calls
                metadata = fetch_tmdb_metadata(file_path.stem)
                if not metadata:
                    pending_files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "folder_context": folder_context,
                        "size": f"{file_path.stat().st_size / (1024**2):.1f} MB" if file_path.exists() else "Unknown"
                    })
            else:
                # Just list all files without checking metadata
                pending_files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "folder_context": folder_context,
                    "size": f"{file_path.stat().st_size / (1024**2):.1f} MB" if file_path.exists() else "Unknown"
                })
        
        return {
            "pending_files": pending_files,
            "count": len(pending_files),
            "message": f"Found {len(pending_files)} video files" + (" needing metadata" if check_metadata else "")
        }
        
    except Exception as e:
        return {"error": f"Failed to get pending files: {e}"}


async def check_pending_metadata(**kwargs):
    """Check which existing files need manual metadata (triggers TMDB lookups)"""
    return await get_pending_files(check_metadata=True, **kwargs)


# ----------------------------
# Utility functions
# ----------------------------


async def send_progress_update(websocket_callback: Optional[Callable], session_id: str, progress_data: Dict):
    """Send progress update via WebSocket and update GlowState tasks"""
    # Update GlowState task if session_id is a task ID
    try:
        from glowos.glow_state import glow_state_store
        state = glow_state_store.get_state()
        
        # Find task by session_id (which should be task_id)
        for task in state.tasks.active:
            if task.id == session_id:
                task.progress = progress_data.get("progress", 0) / 100.0 if progress_data.get("progress", 0) > 1 else progress_data.get("progress", 0)
                task.message = progress_data.get("message", "")
                if progress_data.get("status") == "error":
                    task.status = "error"
                elif progress_data.get("status") in ["done", "complete"]:
                    task.status = "done"
                    task.progress = 1.0
                break
        
        glow_state_store.replace(state)
    except Exception as e:
        print(f"⚠️ Failed to update GlowState task: {e}")
    
    # Send WebSocket update if available
    if websocket_callback:
        try:
            await websocket_callback({
                **progress_data,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"❌ Failed to send progress update: {e}")


async def process_rip_with_progress(full_rip: bool = True, websocket_callback: Optional[Callable] = None, 
                                  session_id: str = "default", **kwargs):
    """
    Enhanced disc processing with WebSocket progress updates
    """
    try:
        print("🔁 Starting disc processing...")
        
        # Get drive path and volume name for folder creation (only used for full rip)
        drive_path = kwargs.get("drive_path")
        volume_name = get_volume_name_from_drive_path(drive_path) if drive_path else None
        print(f"🎯 Volume name detected: {volume_name}")
        
        await send_progress_update(websocket_callback, session_id, {
            "progress": 0,
            "status": "initializing",
            "message": "Starting disc processing..."
        })

        # Check initial directory state
        try:
            files = list(Path(MOVIES_FOLDER).iterdir())
            if not files:
                print(f"⚠️ No files found in {MOVIES_FOLDER}")
            else:
                print(f"📂 Contents of {MOVIES_FOLDER}:")
                for f in files:
                    print(f"   - {f.name}")
        except Exception as e:
            print(f"❌ Failed to read directory {MOVIES_FOLDER}: {e}")
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": f"Cannot read MOVIES_FOLDER: {e}"
            })
            return {"error": f"Cannot read MOVIES_FOLDER: {e}"}

        # Step 1: Rip disc if requested
        rip_destination = None
        if full_rip:
            await send_progress_update(websocket_callback, session_id, {
                "progress": 10,
                "status": "ripping",
                "message": "Ripping disc with MakeMKV..."
            })
            
            success, rip_destination = run_makemkv(volume_name)
            if not success:
                await send_progress_update(websocket_callback, session_id, {
                    "progress": 0,
                    "status": "error",
                    "message": "MakeMKV failed to rip disc"
                })
                return {"error": "MakeMKV failed"}
            
            await send_progress_update(websocket_callback, session_id, {
                "progress": 40,
                "status": "ripping_complete",
                "message": f"Disc ripping completed to {rip_destination}, waiting for file system..."
            })
            
            # Wait for files to settle
            time.sleep(5)
        else:
            print("▶️ Skipping MakeMKV ripping; proceeding with post-processing of entire Movies folder")
            await send_progress_update(websocket_callback, session_id, {
                "progress": 40,
                "status": "skipping_rip",
                "message": "Skipping disc rip, scanning entire Movies folder for processing..."
            })

        # Step 2: Find ripped files
        await send_progress_update(websocket_callback, session_id, {
            "progress": 50,
            "status": "scanning",
            "message": "Recursively scanning for video files..."
        })
        
        # For post-processing, scan the entire movies folder recursively
        # For full rip, look in the specific rip destination if available
        if not full_rip:
            # Post-processing mode: scan entire movies folder
            ripped_files = get_ripped_files()
            scan_location = "entire Movies folder"
        elif rip_destination and os.path.exists(rip_destination):
            # Full rip mode: look in specific destination
            ripped_files = get_ripped_files(rip_destination)
            scan_location = f"rip destination ({rip_destination})"
        else:
            # Fallback: scan entire movies folder
            ripped_files = get_ripped_files()
            scan_location = "Movies folder"

        print(f"📂 Scanned {scan_location} and found {len(ripped_files)} video files")

        if not ripped_files:
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": "No MKV/MP4 files found for processing"
            })
            return {"error": "No video files found"}

        await send_progress_update(websocket_callback, session_id, {
            "progress": 60,
            "status": "processing",
            "message": f"Found {len(ripped_files)} files, fetching metadata..."
        })

        # Step 3: Process each file
        missing_metadata_files = []
        fallback_files = []
        processed_count = 0
        total_files = len(ripped_files)

        for i, (file_path, folder_context) in enumerate(ripped_files):
            file_progress = 60 + (30 * i / total_files)  # 60-90% for file processing
            
            await send_progress_update(websocket_callback, session_id, {
                "progress": file_progress,
                "status": "processing_file",
                "message": f"Processing: {file_path.name} ({i+1}/{total_files})"
            })
            
            print(f"📁 Processing: {file_path.name} | Folder: {folder_context or 'Root'}")
            metadata = fetch_tmdb_metadata(file_path.stem)
            
            if not metadata:
                print(f"⚠️ TMDB metadata not found for {file_path.name}, checking for fallback options...")
                
                # Use folder context for fallback naming
                context_name = folder_context or volume_name
                
                if context_name and detect_media_type_from_folder(context_name) == "tv":
                    # This is a TV show that needs episode numbering
                    track_match = re.search(r'_t(\d+)', file_path.stem)
                    track_number = track_match.group(1) if track_match else str(i + 1)
                    
                    fallback_files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "track_number": track_number,
                        "suggested_episode": track_number.zfill(2),
                        "folder_context": context_name
                    })
                    continue
                    
                elif context_name:
                    # This is likely a movie, use simple fallback
                    pretty_name = create_pretty_filename_from_folder(context_name)
                    media_type = detect_media_type_from_folder(context_name)
                    
                    fallback_metadata = {
                        "title": pretty_name,
                        "year": "Unknown",
                        "type": media_type
                    }
                    
                    print(f"📝 Using folder-based fallback metadata: {fallback_metadata}")
                    metadata = fallback_metadata
                else:
                    print(f"⚠️ No folder context available for fallback naming of {file_path.name}")
                    missing_metadata_files.append(file_path.name)
                    continue

            # Process files with metadata (either TMDB or movie fallback)
            if metadata:
                new_name = rename_to_plex_format(file_path.name, metadata)
                dest_folder = determine_plex_destination(metadata["title"], metadata["type"], folder_context)
                dest_path = Path(PLEX_BASE) / dest_folder
                dest_path.mkdir(parents=True, exist_ok=True)

                target = dest_path / new_name
                
                # Handle duplicate filenames by adding a number
                counter = 1
                original_target = target
                while target.exists():
                    name_part = original_target.stem
                    extension = original_target.suffix
                    target = original_target.parent / f"{name_part} ({counter}){extension}"
                    counter += 1
                
                try:
                    shutil.move(str(file_path), target)
                    print(f"✅ Moved {file_path.name} to {target}")
                    processed_count += 1
                except Exception as e:
                    print(f"❌ Failed to move {file_path.name}: {e}")
                    missing_metadata_files.append(file_path.name)

        # Check if we have files that need episode numbering
        if fallback_files:
            print(f"📺 Found {len(fallback_files)} TV show files needing episode numbers")
            
            # Group files by folder context for better organization
            grouped_files = {}
            for file_info in fallback_files:
                context = file_info["folder_context"]
                if context not in grouped_files:
                    grouped_files[context] = []
                grouped_files[context].append(file_info)
            
            # Store session state for resumption
            pending_sessions[session_id] = {
                "fallback_files": fallback_files,
                "grouped_files": grouped_files,
                "websocket_callback": websocket_callback,
                "processed_count": processed_count,
                "total_files": total_files,
                "missing_metadata_files": missing_metadata_files
            }
            
            # Send episode numbering request
            await send_progress_update(websocket_callback, session_id, {
                "progress": 75,
                "status": "awaiting_episode_numbers",
                "message": f"Need episode numbers for {len(fallback_files)} TV show files from {len(grouped_files)} folder(s)",
                "fallback_files": fallback_files,
                "grouped_files": grouped_files,
                "action_required": "episode_numbering"
            })
            
            return {
                "status": "awaiting_input",
                "message": "Episode numbering required",
                "session_id": session_id,
                "fallback_files": fallback_files,
                "grouped_files": grouped_files
            }

        # Continue with Plex scan if no episode numbering needed
        return await finish_processing(websocket_callback, session_id, processed_count, total_files, missing_metadata_files)

    except Exception as e:
        await send_progress_update(websocket_callback, session_id, {
            "progress": 0,
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        })
        
        print(f"❌ Disc processing error: {e}")
        return {"error": f"Disc processing failed: {e}", "success": False}


async def resume_processing_with_episodes(session_id: str, episode_mappings: Dict[str, str], **kwargs):
    """
    Resume processing after receiving episode number mappings
    episode_mappings: {"filename1.mkv": "01", "filename2.mkv": "02", ...}
    """
    try:
        # Get the stored session data
        if session_id not in pending_sessions:
            return {"error": "Session not found or expired"}
        
        session_data = pending_sessions[session_id]
        fallback_files = session_data["fallback_files"]
        websocket_callback = session_data["websocket_callback"]
        processed_count = session_data["processed_count"]
        total_files = session_data["total_files"]
        missing_metadata_files = session_data["missing_metadata_files"]
        
        print(f"📺 Resuming processing with episode mappings: {episode_mappings}")
        
        await send_progress_update(websocket_callback, session_id, {
            "progress": 80,
            "status": "processing_episodes",
            "message": "Processing TV show files with episode numbers..."
        })
        
        # Process each fallback file with its assigned episode number
        for file_info in fallback_files:
            filename = file_info["filename"]
            episode_number = episode_mappings.get(filename)
            folder_context = file_info["folder_context"]
            
            if not episode_number:
                print(f"⚠️ No episode number provided for {filename}, skipping")
                missing_metadata_files.append(filename)
                continue
            
            print(f"📺 Processing {filename} as episode {episode_number} (folder: {folder_context})")
            
            # Create metadata with episode number
            pretty_name = create_pretty_filename_from_folder(folder_context, episode_number=episode_number)
            
            # Extract season and episode info
            season_match = re.search(r'S(\d+)', pretty_name)
            episode_match = re.search(r'E(\d+)', pretty_name)
            clean_title = re.sub(r'\s*S\d+E\d+.*$', '', pretty_name)
            
            metadata = {
                "title": clean_title,
                "year": "Unknown",
                "type": "tv",
                "season": season_match.group(1) if season_match else "01",
                "episode": episode_match.group(1) if episode_match else episode_number.zfill(2)
            }
            
            # Find the actual file
            file_path = Path(file_info["path"])
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                missing_metadata_files.append(filename)
                continue
            
            # Create new name and move file
            new_name = rename_to_plex_format(filename, metadata)
            dest_folder = determine_plex_destination(clean_title, "tv", folder_context)
            dest_path = Path(PLEX_BASE) / dest_folder
            dest_path.mkdir(parents=True, exist_ok=True)

            target = dest_path / new_name
            
            # Handle duplicate filenames
            counter = 1
            original_target = target
            while target.exists():
                name_part = original_target.stem
                extension = original_target.suffix
                target = original_target.parent / f"{name_part} ({counter}){extension}"
                counter += 1
            
            try:
                shutil.move(str(file_path), target)
                print(f"✅ Moved {filename} to {target}")
                processed_count += 1
            except Exception as e:
                print(f"❌ Failed to move {filename}: {e}")
                missing_metadata_files.append(filename)

        # Clean up session data
        del pending_sessions[session_id]
        
        # Continue with final processing
        return await finish_processing(websocket_callback, session_id, processed_count, total_files, missing_metadata_files)
        
    except Exception as e:
        print(f"❌ Error resuming processing: {e}")
        # Clean up session data on error
        if session_id in pending_sessions:
            del pending_sessions[session_id]
        
        await send_progress_update(websocket_callback, session_id, {
            "progress": 0,
            "status": "error",
            "message": f"Failed to resume processing: {str(e)}"
        })
        
        return {"error": f"Failed to resume processing: {str(e)}"}


async def finish_processing(websocket_callback: Optional[Callable], session_id: str, 
                          processed_count: int, total_files: int, missing_metadata_files: List[str]):
    """
    Complete the processing workflow with Plex scan and final status
    """
    # Step 4: Trigger Plex scan
    await send_progress_update(websocket_callback, session_id, {
        "progress": 90,
        "status": "scanning_plex",
        "message": "Triggering Plex library scan..."
    })
    
    try:
        # Import Plex superpower and trigger scan
        from superpowers.Plex.main import Superpower as PlexSuperpower
        plex_power = PlexSuperpower()
        
        # Scan relevant libraries
        libraries_result = await plex_power.run("list_plex_libraries")
        if "libraries" in libraries_result:
            for lib in libraries_result.get("libraries", []):
                if lib.get("title", "").lower() in ["movies", "tv shows"]:
                    await plex_power.run("scan_plex", key=lib.get("key"))
                    
    except Exception as e:
        print(f"⚠️ Plex scan failed: {e}")

    # Step 5: Complete
    if missing_metadata_files:
        await send_progress_update(websocket_callback, session_id, {
            "progress": 100,
            "status": "partial_success",
            "message": f"Processed {processed_count}/{total_files} files. {len(missing_metadata_files)} need manual metadata.",
            "missing_files": missing_metadata_files,
            "processed_count": processed_count,
            "total_files": total_files
        })
        
        return {
            "status": "partial_success",
            "message": "Some files need manual metadata input",
            "files": missing_metadata_files,
            "processed_count": processed_count,
            "total_files": total_files
        }

    await send_progress_update(websocket_callback, session_id, {
        "progress": 100,
        "status": "complete",
        "message": f"Successfully processed all {processed_count} files and added to Plex!",
        "processed_count": processed_count,
        "total_files": total_files,
        "completion_actions": {
            "show_next_steps": True,
            "processed_files": [f"Processed {processed_count} files"],
            "plex_folders": {
                "movies": str(Path(PLEX_BASE) / "Movies"),
                "tv_shows": str(Path(PLEX_BASE) / "Tv Shows")
            }
        }
    })

    return {
        "status": "success", 
        "message": "Disc processed and added to Plex",
        "processed_count": processed_count,
        "total_files": total_files,
        "completion_actions": {
            "show_next_steps": True,
            "processed_files": [f"Processed {processed_count} files"],
            "plex_folders": {
                "movies": str(Path(PLEX_BASE) / "Movies"),
                "tv_shows": str(Path(PLEX_BASE) / "Tv Shows")
            }
        }
    }


async def process_manual_metadata_with_progress(filename: str, manual_title: str, 
                                              websocket_callback: Optional[Callable] = None,
                                              session_id: str = "manual", **kwargs):
    """
    Enhanced manual metadata processing with progress updates
    """
    try:
        await send_progress_update(websocket_callback, session_id, {
            "progress": 0,
            "status": "initializing",
            "message": f"Starting manual metadata processing for: {filename}"
        })

        # Look for the file in the entire movies folder structure
        file_path = None
        for root, dirs, files in os.walk(MOVIES_FOLDER):
            if filename in files:
                file_path = Path(root) / filename
                break
        
        if not file_path or not file_path.exists():
            error_msg = f"❌ File '{filename}' not found in {MOVIES_FOLDER} or its subdirectories"
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": error_msg
            })
            return {"status": "error", "error": error_msg}

        print(f"🧐 Found file at: {file_path}")

        # Step 1: Fetch TMDB metadata
        await send_progress_update(websocket_callback, session_id, {
            "progress": 20,
            "status": "fetching_metadata",
            "message": f"Fetching metadata for: {manual_title}"
        })
        
        metadata = fetch_tmdb_metadata(manual_title)
        print(f"🎬 TMDB metadata for '{manual_title}': {metadata}")
        
        if not metadata:
            error_msg = f"❌ Could not find metadata for title '{manual_title}'"
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": error_msg
            })
            return {"status": "error", "error": error_msg}

        # Step 2: Rename to Plex format
        await send_progress_update(websocket_callback, session_id, {
            "progress": 40,
            "status": "renaming",
            "message": "Converting to Plex-compatible format..."
        })
        
        new_name = rename_to_plex_format(filename, metadata)
        print(f"📝 Plex-compatible filename: {new_name}")
        
        if not new_name or not new_name.endswith((".mkv", ".mp4")):
            error_msg = f"❌ Failed to rename '{filename}' using Plex format"
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": error_msg
            })
            return {"status": "error", "error": error_msg}

        # Step 3: Determine destination and move file
        await send_progress_update(websocket_callback, session_id, {
            "progress": 60,
            "status": "moving",
            "message": "Moving file to Plex library..."
        })
        
        dest_folder = determine_plex_destination(metadata["title"], metadata["type"], None)
        dest_path = Path(PLEX_BASE) / dest_folder
        dest_path.mkdir(parents=True, exist_ok=True)

        target = dest_path / new_name
        print(f"🚚 Moving file to: {target}")

        try:
            shutil.move(str(file_path), target)
            print(f"✅ File moved to {target}")
        except Exception as e:
            error_msg = f"❌ Failed to move file: {str(e)}"
            await send_progress_update(websocket_callback, session_id, {
                "progress": 0,
                "status": "error",
                "message": error_msg
            })
            return {"status": "error", "error": error_msg}

        # Step 4: Trigger Plex scan
        await send_progress_update(websocket_callback, session_id, {
            "progress": 80,
            "status": "scanning_plex",
            "message": "Triggering Plex library scan..."
        })
        
        try:
            from superpowers.Plex.main import Superpower as PlexSuperpower
            plex_power = PlexSuperpower()
            
            libraries_result = await plex_power.run("list_plex_libraries")
            if "libraries" in libraries_result:
                for lib in libraries_result.get("libraries", []):
                    if any(word in lib.get("title", "").lower() for word in ["movie", "tv"]):
                        print(f"📡 Triggering scan for: {lib.get('title')} ({lib.get('key')})")
                        await plex_power.run("scan_plex", key=lib.get("key"))
                        
        except Exception as e:
            print(f"⚠️ Plex scan failed: {e}")
            await send_progress_update(websocket_callback, session_id, {
                "progress": 100,
                "status": "warning",
                "message": f"✅ File moved successfully, but Plex scan failed: {e}",
                "target": str(target),
                "metadata": metadata
            })
            return {
                "status": "warning",
                "message": f"✅ File moved, but failed to trigger Plex scan: {e}",
                "target": str(target),
                "metadata": metadata
            }

        # Step 5: Complete
        await send_progress_update(websocket_callback, session_id, {
            "progress": 100,
            "status": "complete",
            "message": f"✅ Successfully processed '{filename}' as '{new_name}'",
            "target": str(target),
            "metadata": metadata
        })

        return {
            "status": "success",
            "message": f"✅ '{filename}' processed and added to Plex as '{new_name}'",
            "target": str(target),
            "metadata": metadata
        }

    except Exception as e:
        error_msg = f"Manual metadata processing failed: {str(e)}"
        await send_progress_update(websocket_callback, session_id, {
            "progress": 0,
            "status": "error",
            "message": error_msg
        })
        print(f"❌ Manual metadata error: {e}")
        return {"error": error_msg, "success": False}


async def get_rip_status(**kwargs):
    """Get current rip status and file information"""
    try:
        # Check if MakeMKV is running
        makemkv_running = False
        try:
            result = subprocess.run(['pgrep', 'makemkvcon'], capture_output=True, text=True)
            makemkv_running = bool(result.stdout.strip())
        except:
            pass

        # Get current files in movies folder (recursive)
        ripped_files = get_ripped_files()
        
        # Check disk usage
        try:
            total, used, free = shutil.disk_usage(MOVIES_FOLDER)
            disk_info = {
                "total": f"{total // (1024**3)} GB",
                "used": f"{used // (1024**3)} GB", 
                "free": f"{free // (1024**3)} GB",
                "usage_percent": round((used / total) * 100, 1)
            }
        except:
            disk_info = {"error": "Could not get disk usage"}

        return {
            "makemkv_running": makemkv_running,
            "movies_folder": MOVIES_FOLDER,
            "ripped_files_count": len(ripped_files),
            "ripped_files": [f"{file_path.name} ({folder_context or 'Root'})" for file_path, folder_context in ripped_files],
            "disk_usage": disk_info,
            "plex_base": PLEX_BASE
        }

    except Exception as e:
        return {"error": f"Failed to get rip status: {e}"}


async def detect_drives(**kwargs):
    """Detect available optical drives and their status"""
    try:
        drives = []
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # Check for mounted volumes that might be optical drives
            try:
                result = subprocess.run(['ls', '/Volumes'], capture_output=True, text=True)
                volumes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                print(f"🔍 Found volumes: {volumes}")
                
                # Also check system_profiler for optical drives
                result = subprocess.run([
                    'system_profiler', 'SPDiscBurningDataType', '-json'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    import json
                    try:
                        profiler_data = json.loads(result.stdout)
                        disc_burning = profiler_data.get('SPDiscBurningDataType', [])
                        
                        for drive in disc_burning:
                            drive_info = {
                                "name": drive.get('_name', 'Unknown Drive'),
                                "device": drive.get('device', ''),
                                "type": "optical",
                                "vendor": drive.get('vendor', ''),
                                "product": drive.get('product', ''),
                                "has_disc": False,
                                "disc_info": None,
                                "mount_point": None
                            }
                            print(f"🔍 Processing drive: {drive_info['name']}")
                            
                            # Check if there's a disc by looking for mounted volumes
                            for volume in volumes:
                                if volume and not volume.startswith('.'):
                                    volume_path = f"/Volumes/{volume}"
                                    print(f"🔍 Checking volume: {volume} at {volume_path}")
                                    if os.path.exists(volume_path):
                                        # Try to detect if this is an optical disc
                                        try:
                                            result = subprocess.run([
                                                'hdiutil', 'info'
                                            ], capture_output=True, text=True)
                                            
                                            if volume in result.stdout:
                                                print(f"✅ Found disc in volume: {volume}")
                                                drive_info["has_disc"] = True
                                                drive_info["mount_point"] = volume_path
                                                drive_info["disc_info"] = {
                                                    "name": volume,
                                                    "path": volume_path,
                                                    "type": "Unknown"
                                                }
                                                break
                                        except Exception as e:
                                            print(f"❌ Error checking volume {volume}: {e}")
                                            pass
                            
                            drives.append(drive_info)
                    except json.JSONDecodeError:
                        pass
                
                # Use MakeMKV to confirm disc presence and extract basic info
                try:
                    mkv = subprocess.run([
                        "/Applications/MakeMKV.app/Contents/MacOS/makemkvcon",
                        "info", "disc:0"
                    ], capture_output=True, text=True, timeout=10)
                    if mkv.returncode == 0 and mkv.stdout:
                        mkv_out = mkv.stdout
                        disc_type = (
                            "Blu-ray" if ("BD" in mkv_out.upper() or "BLU" in mkv_out.upper())
                            else ("DVD" if "DVD" in mkv_out.upper() else None)
                        )
                        title = None
                        for line in mkv_out.splitlines():
                            if 'TINFO:0,27,0,' in line:
                                title_part = line.split(',')[-1].strip('"')
                                if title_part and title_part.lower() != "unknown":
                                    title = title_part
                                break

                        # Guess mount point from volumes
                        mount_point = None
                        for v in volumes:
                            vp = f"/Volumes/{v}"
                            if os.path.exists(os.path.join(vp, "BDMV")) or os.path.exists(os.path.join(vp, "VIDEO_TS")):
                                mount_point = vp
                                break
                        if not mount_point and title:
                            for v in volumes:
                                if v.strip().upper() == title.strip().upper():
                                    mount_point = f"/Volumes/{v}"
                                    break

                        # Annotate first detected drive or create a minimal one
                        if drives:
                            drives[0]["has_disc"] = True
                            drives[0]["mount_point"] = mount_point or drives[0]["mount_point"]
                            existing_info = drives[0]["disc_info"] or {}
                            drives[0]["disc_info"] = {
                                "name": title or existing_info.get("name") or "Disc",
                                "path": mount_point or drives[0]["mount_point"],
                                "type": disc_type or existing_info.get("type") or "Unknown"
                            }
                        else:
                            drives.append({
                                "name": "MakeMKV Optical Drive",
                                "device": "disc:0",
                                "type": "optical",
                                "vendor": "Unknown",
                                "product": "Optical Drive",
                                "has_disc": True,
                                "disc_info": {
                                    "name": title or "Disc",
                                    "path": mount_point,
                                    "type": disc_type or "Unknown"
                                },
                                "mount_point": mount_point
                            })
                except Exception as e:
                    print(f"⚠️ MakeMKV probe failed: {e}")

                # Final fallback: if we see any non-system volume, assume it's the disc
                try:
                    if not any(d.get("has_disc") for d in drives):
                        candidate = next((v for v in volumes if v and v not in ["Macintosh HD", "Recovery"] and not v.startswith('.')), None)
                        if candidate:
                            mount_point = f"/Volumes/{candidate}"
                            pretty_name = candidate.replace('_', ' ').title()
                            if drives:
                                drives[0]["has_disc"] = True
                                drives[0]["mount_point"] = mount_point
                                drives[0]["disc_info"] = {
                                    "name": pretty_name,
                                    "path": mount_point,
                                    "type": drives[0].get("disc_info", {}).get("type") or "Unknown"
                                }
                            else:
                                drives.append({
                                    "name": "Optical Drive",
                                    "device": mount_point,
                                    "type": "optical",
                                    "vendor": "Unknown",
                                    "product": "Mounted Volume",
                                    "has_disc": True,
                                    "disc_info": {
                                        "name": pretty_name,
                                        "path": mount_point,
                                        "type": "Unknown"
                                    },
                                    "mount_point": mount_point
                                })
                except Exception:
                    pass
                
                # If no optical drives found via system_profiler, check for any mounted optical media
                if not drives:
                    print("🔍 No optical drives found, checking volumes directly")
                    for volume in volumes:
                        if volume and not volume.startswith('.'):
                            volume_path = f"/Volumes/{volume}"
                            print(f"🔍 Checking direct volume: {volume}")
                            if os.path.exists(volume_path):
                                # Check if this volume contains DVD/Blu-ray structure
                                has_video_ts = os.path.exists(os.path.join(volume_path, "VIDEO_TS"))
                                has_bdmv = os.path.exists(os.path.join(volume_path, "BDMV"))
                                
                                print(f"🔍 Volume {volume}: VIDEO_TS={has_video_ts}, BDMV={has_bdmv}")
                                
                                if has_video_ts or has_bdmv:
                                    print(f"✅ Found disc structure in volume: {volume}")
                                    # Basic drive info for mounted volumes
                                    drives.append({
                                        "name": f"Volume: {volume}",
                                        "device": volume_path,
                                        "type": "volume",
                                        "vendor": "Unknown",
                                        "product": "Mounted Volume",
                                        "has_disc": True,
                                        "disc_info": {
                                            "name": volume,
                                            "path": volume_path,
                                            "type": "DVD" if has_video_ts else "Blu-ray"
                                        },
                                        "mount_point": volume_path
                                    })
                                else:
                                    # Still add as potential drive but without disc
                                    drives.append({
                                        "name": f"Volume: {volume}",
                                        "device": volume_path,
                                        "type": "volume", 
                                        "vendor": "Unknown",
                                        "product": "Mounted Volume",
                                        "has_disc": False,
                                        "disc_info": None,
                                        "mount_point": volume_path
                                    })
                        
            except Exception as e:
                print(f"Error detecting macOS drives: {e}")
                
        elif system == "linux":
            # Linux drive detection
            try:
                # Check /proc/sys/dev/cdrom/info for CD-ROM drives
                if os.path.exists("/proc/sys/dev/cdrom/info"):
                    with open("/proc/sys/dev/cdrom/info", "r") as f:
                        cdrom_info = f.read()
                    
                    # Parse drive names from the info
                    for line in cdrom_info.split('\n'):
                        if line.startswith('drive name:'):
                            drive_names = line.split(':')[1].strip().split()
                            for drive_name in drive_names:
                                device_path = f"/dev/{drive_name}"
                                drives.append({
                                    "name": drive_name,
                                    "device": device_path,
                                    "type": "optical",
                                    "vendor": "Unknown",
                                    "product": "CD/DVD Drive",
                                    "has_disc": os.path.exists(device_path),
                                    "disc_info": None,
                                    "mount_point": None
                                })
            except Exception as e:
                print(f"Error detecting Linux drives: {e}")
                
        # Fallback: Check common optical drive paths
        common_paths = ["/dev/cdrom", "/dev/dvd", "/dev/sr0", "/dev/disk1", "/dev/disk2"]
        if not drives:
            for path in common_paths:
                if os.path.exists(path):
                    drives.append({
                        "name": f"Drive at {path}",
                        "device": path,
                        "type": "optical",
                        "vendor": "Unknown",
                        "product": "Optical Drive",
                        "has_disc": True,  # Assume disc present if device exists
                        "disc_info": None,
                        "mount_point": None
                    })
        
        print(f"🔍 Final drives list: {len(drives)} drives")
        for i, drive in enumerate(drives):
            print(f"🔍 Drive {i}: {drive['name']} - has_disc: {drive['has_disc']}")
        
        return {
            "drives": drives,
            "count": len(drives),
            "message": f"Found {len(drives)} optical drive(s)" if drives else "No optical drives detected"
        }
        
    except Exception as e:
        return {"error": f"Failed to detect drives: {e}"}


async def get_disc_info(drive_path: str = None, **kwargs):
    """Get information about the disc in the drive"""
    try:
        disc_info = {
            "has_disc": False,
            "disc_type": None,
            "title": None,
            "size": None,
            "tracks": [],
            "estimated_runtime": None
        }
        
        # Try to detect disc using various methods
        if drive_path:
            # Method 1: Check if it's a mounted volume with video files
            if os.path.exists(drive_path):
                try:
                    # Look for common video disc structures
                    video_ts_path = os.path.join(drive_path, "VIDEO_TS")
                    bdmv_path = os.path.join(drive_path, "BDMV")
                    
                    if os.path.exists(video_ts_path):
                        disc_info.update({
                            "has_disc": True,
                            "disc_type": "DVD",
                            "title": os.path.basename(drive_path),
                            "structure": "VIDEO_TS"
                        })
                        
                        # Try to get size info
                        try:
                            total_size = sum(
                                os.path.getsize(os.path.join(video_ts_path, f))
                                for f in os.listdir(video_ts_path)
                                if os.path.isfile(os.path.join(video_ts_path, f))
                            )
                            disc_info["size"] = f"{total_size / (1024**3):.2f} GB"
                        except:
                            pass
                            
                    elif os.path.exists(bdmv_path):
                        disc_info.update({
                            "has_disc": True,
                            "disc_type": "Blu-ray",
                            "title": os.path.basename(drive_path),
                            "structure": "BDMV"
                        })
                        
                        # Try to get size info
                        try:
                            total_size = 0
                            for root, dirs, files in os.walk(bdmv_path):
                                total_size += sum(
                                    os.path.getsize(os.path.join(root, f))
                                    for f in files
                                )
                            disc_info["size"] = f"{total_size / (1024**3):.2f} GB"
                        except:
                            pass
                    
                    else:
                        # Generic disc detection
                        files = os.listdir(drive_path)
                        if files:
                            disc_info.update({
                                "has_disc": True,
                                "disc_type": "Data Disc",
                                "title": os.path.basename(drive_path),
                                "file_count": len(files)
                            })
                            
                except Exception as e:
                    print(f"Error reading disc at {drive_path}: {e}")
        
        # Method 2: Try MakeMKV info if available
        try:
            result = subprocess.run([
                "/Applications/MakeMKV.app/Contents/MacOS/makemkvcon", 
                "info", "disc:0"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                disc_info["has_disc"] = True
                if "DVD" in result.stdout.upper():
                    disc_info["disc_type"] = "DVD"
                elif "BD" in result.stdout.upper() or "BLU" in result.stdout.upper():
                    disc_info["disc_type"] = "Blu-ray"
                
                # Try to extract title from MakeMKV output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TINFO:0,27,0,' in line:  # MakeMKV title info
                        title_part = line.split(',')[-1].strip('"')
                        if title_part and title_part != "unknown":
                            disc_info["title"] = title_part
                        break
                        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except Exception as e:
            print(f"MakeMKV info failed: {e}")
        
        return disc_info
        
    except Exception as e:
        return {"error": f"Failed to get disc info: {e}"}


async def eject_disc(drive_path: str = None, **kwargs):
    """Eject the disc from the drive"""
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            if drive_path and drive_path.startswith("/Volumes/"):
                # Unmount the volume
                result = subprocess.run(['diskutil', 'eject', drive_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return {"success": True, "message": f"Ejected disc from {drive_path}"}
                else:
                    return {"error": f"Failed to eject: {result.stderr}"}
            else:
                # Try to eject first optical drive
                result = subprocess.run(['drutil', 'eject'], capture_output=True, text=True)
                if result.returncode == 0:
                    return {"success": True, "message": "Ejected disc"}
                else:
                    return {"error": f"Failed to eject: {result.stderr}"}
        
        elif system == "linux":
            # Linux eject command
            result = subprocess.run(['eject'], capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "message": "Ejected disc"}
            else:
                return {"error": f"Failed to eject: {result.stderr}"}
        
        else:
            return {"error": f"Eject not supported on {system}"}
            
    except Exception as e:
        return {"error": f"Failed to eject disc: {e}"}


async def check_makemkv_status(**kwargs):
    """Check if MakeMKV is installed and accessible"""
    try:
        makemkv_path = "/Applications/MakeMKV.app/Contents/MacOS/makemkvcon"
        
        status = {
            "installed": False,
            "version": None,
            "path": makemkv_path,
            "accessible": False,
            "running": False
        }
        
        # Check if MakeMKV exists
        if os.path.exists(makemkv_path):
            status["installed"] = True
            status["accessible"] = True
            
            try:
                # Get version info
                result = subprocess.run([makemkv_path, "--help"], 
                                      capture_output=True, text=True, timeout=10)
                if "MakeMKV" in result.stdout:
                    # Try to extract version
                    for line in result.stdout.split('\n'):
                        if 'version' in line.lower():
                            status["version"] = line.strip()
                            break
                    if not status["version"]:
                        status["version"] = "Unknown version"
            except:
                status["version"] = "Unknown version"
        
        # Check if MakeMKV is currently running
        try:
            result = subprocess.run(['pgrep', '-f', 'makemkv'], 
                                  capture_output=True, text=True)
            status["running"] = bool(result.stdout.strip())
        except:
            pass
            
        return status
        
    except Exception as e:
        return {"error": f"Failed to check MakeMKV status: {e}"}


# Add disk usage check for the movies folder
async def get_movies_folder_info(**kwargs):
    """Get information about the movies folder"""
    try:
        info = {
            "path": MOVIES_FOLDER,
            "exists": os.path.exists(MOVIES_FOLDER),
            "accessible": False,
            "files": [],
            "disk_usage": None,
            "free_space": None
        }
        
        if info["exists"]:
            try:
                # Check if we can access the folder
                os.listdir(MOVIES_FOLDER)
                info["accessible"] = True
                
                # Get files recursively
                video_files = []
                for file_path, folder_context in get_ripped_files():
                    video_files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "folder_context": folder_context,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
                
                info["files"] = video_files
                
                # Get disk usage
                total, used, free = shutil.disk_usage(MOVIES_FOLDER)
                info["disk_usage"] = {
                    "total": f"{total // (1024**3)} GB",
                    "used": f"{used // (1024**3)} GB",
                    "free": f"{free // (1024**3)} GB",
                    "usage_percent": round((used / total) * 100, 1)
                }
                info["free_space"] = f"{free // (1024**3)} GB"
                
            except PermissionError:
                info["accessible"] = False
            except Exception as e:
                print(f"Error accessing movies folder: {e}")
        
        return info
        
    except Exception as e:
        return {"error": f"Failed to get movies folder info: {e}"}


async def trigger_plex_scan(**kwargs):
    """Trigger Plex library scan for Movies and TV Shows"""
    try:
        from superpowers.Plex.main import Superpower as PlexSuperpower
        plex_power = PlexSuperpower()
        
        libraries_result = await plex_power.run("list_plex_libraries")
        scanned_libraries = []
        
        if "libraries" in libraries_result:
            for lib in libraries_result.get("libraries", []):
                if any(word in lib.get("title", "").lower() for word in ["movie", "tv"]):
                    scan_result = await plex_power.run("scan_plex", key=lib.get("key"))
                    scanned_libraries.append(lib.get("title", ""))
                    
        return {
            "success": True,
            "message": f"Triggered scan for {len(scanned_libraries)} libraries",
            "scanned_libraries": scanned_libraries
        }
        
    except Exception as e:
        return {"error": f"Failed to trigger Plex scan: {e}"}


# ----------------------------
# Superpower Wrapper
# ----------------------------
class Superpower:
    name = "ripdisc"
    description = "Rip DVDs/Blu-rays with MakeMKV and automatically organize them for Plex"
    
    # Define what this superpower can handle
    intent_map = {
        "rip_disc": "Rip a disc and process it for Plex (full workflow)",
        "post_process": "Process existing ripped files (skip MakeMKV step)",
        "manual_metadata": "Manually assign metadata to a specific file",
        "set_episode_numbers": "Set episode numbers for TV show files and resume processing",
        "get_rip_status": "Check current ripping status and file information", 
        "get_pending_files": "List video files in movies folder (no metadata checking)",
        "check_pending_metadata": "Check which files need manual metadata (triggers TMDB lookups)",
        "scan_movies_folder": "Scan the movies folder for ripped files",
        "detect_drives": "Detect available optical drives and their status",
        "get_disc_info": "Get information about the disc in the drive",
        "eject_disc": "Eject the disc from the drive",
        "check_makemkv_status": "Check MakeMKV installation and status",
        "get_movies_folder_info": "Get detailed information about the movies folder",
        "scan_plex": "Trigger Plex library scan for processed content"
    }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        print(f"🎯 RipDisc superpower called with intent: {intent}, kwargs: {kwargs}")
        
        try:
            if intent == "rip_disc":
                # Full rip workflow with WebSocket support
                mode = kwargs.get("mode", "full_rip")
                full_rip = mode == "full_rip"
                
                # Remove parameters we're explicitly passing to avoid duplication
                clean_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ["mode", "websocket_callback", "session_id"]}
                
                return await process_rip_with_progress(
                    full_rip=full_rip,
                    websocket_callback=kwargs.get("websocket_callback"),
                    session_id=kwargs.get("session_id", "ripdisc"),
                    **clean_kwargs
                )
                
            elif intent == "post_process":
                # Process existing files without ripping - scan entire Movies folder
                clean_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ["mode", "websocket_callback", "session_id"]}
                
                return await process_rip_with_progress(
                    full_rip=False,
                    websocket_callback=kwargs.get("websocket_callback"),
                    session_id=kwargs.get("session_id", "postprocess"),
                    **clean_kwargs
                )
                
            elif intent == "set_episode_numbers":
                # Resume processing with episode numbers
                session_id = kwargs.get("session_id")
                episode_mappings = kwargs.get("episode_mappings", {})
                
                if not session_id:
                    return {"error": "Session ID is required for episode numbering"}
                    
                if not episode_mappings:
                    return {"error": "Episode mappings are required"}
                
                # Remove parameters we're explicitly passing to avoid duplication
                clean_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ["session_id", "episode_mappings"]}
                
                return await resume_processing_with_episodes(session_id, episode_mappings, **clean_kwargs)
                
            elif intent == "manual_metadata":
                # Manual metadata assignment with progress
                filename = kwargs.get("filename")
                title = kwargs.get("title")
                
                if not filename or not title:
                    return {"error": "Both filename and title are required for manual metadata"}
                
                return await process_manual_metadata_with_progress(
                    filename=filename,
                    manual_title=title,
                    websocket_callback=kwargs.get("websocket_callback"),
                    session_id=kwargs.get("session_id", "manual"),
                    **kwargs
                )
                
            elif intent == "get_rip_status":
                return await get_rip_status(**kwargs)
                
            elif intent == "get_pending_files":
                return await get_pending_files(**kwargs)
                
            elif intent == "check_pending_metadata":
                return await check_pending_metadata(**kwargs)
                
            elif intent == "scan_movies_folder":
                # Return file info with folder context
                ripped_files = get_ripped_files()
                return {
                    "files_found": len(ripped_files),
                    "files": [{"filename": file_path.name, "folder": folder_context or "Root"} for file_path, folder_context in ripped_files],
                    "movies_folder": MOVIES_FOLDER
                }
                
            elif intent == "detect_drives":
                return await detect_drives(**kwargs)
                
            elif intent == "get_disc_info":
                return await get_disc_info(**kwargs)
                
            elif intent == "eject_disc":
                return await eject_disc(**kwargs)
                
            elif intent == "check_makemkv_status":
                return await check_makemkv_status(**kwargs)
                
            elif intent == "get_movies_folder_info":
                return await get_movies_folder_info(**kwargs)
                
            elif intent == "scan_plex":
                return await trigger_plex_scan(**kwargs)
                
            else:
                return {"error": f"Unknown RipDisc intent: {intent}"}
                
        except Exception as e:
            print(f"❌ RipDisc superpower error: {e}")
            return {"error": f"RipDisc superpower error: {str(e)}"}