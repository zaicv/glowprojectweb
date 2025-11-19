import os
import shutil
import glob
from pathlib import Path
import json
from typing import Optional, List, Dict, Any
import asyncio
import base64
import mimetypes


class Superpower:
    name = "file_ops"
    
    # Define what this superpower can handle
    intent_map = {
        "move_file": "Move a file from one location to another",
        "copy_file": "Copy a file to a new location",
        "rename_file": "Rename a file or directory",
        "bulk_rename": "Rename multiple files with a pattern",
        "delete_file": "Delete a file or directory",
        "create_directory": "Create a new directory",
        "list_files": "List files in a directory",
        "find_files": "Find files matching a pattern",
        "search_files": "Search for files or folders by name with location hints",
        "get_file_info": "Get information about a file or directory",
        "organize_files": "Organize files by type or date",
        "upload_file": "Upload a file to the server",
        "upload_base64_file": "Upload a base64 encoded file to the server",
        "download_file": "Prepare a file for download and return base64 content",
        "get_download_url": "Get a secure download URL for a file",
    }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        print(f"📁 File ops superpower called with intent: {intent}, kwargs: {kwargs}")
        
        try:
            if intent == "move_file":
                return await self.move_file(**kwargs)
            elif intent == "copy_file":
                return await self.copy_file(**kwargs)
            elif intent == "rename_file":
                return await self.rename_file(**kwargs)
            elif intent == "bulk_rename":
                return await self.bulk_rename(**kwargs)
            elif intent == "delete_file":
                return await self.delete_file(**kwargs)
            elif intent == "create_directory":
                return await self.create_directory(**kwargs)
            elif intent == "list_files":
                return await self.list_files(**kwargs)
            elif intent == "find_files":
                return await self.find_files(**kwargs)
            elif intent == "search_files":
                return await self.search_files(**kwargs)
            elif intent == "get_file_info":
                return await self.get_file_info(**kwargs)
            elif intent == "organize_files":
                return await self.organize_files(**kwargs)
            elif intent == "upload_file":
                return await self.upload_file(**kwargs)
            elif intent == "upload_base64_file":
                return await self.upload_base64_file(**kwargs)
            elif intent == "download_file":
                return await self.download_file(**kwargs)
            elif intent == "get_download_url":
                return await self.get_download_url(**kwargs)
            else:
                return {"error": f"Unknown file ops intent: {intent}"}
        except Exception as e:
            return {"error": f"File operation failed: {str(e)}"}

    async def download_file(self, file_path: str, **kwargs):
        """Download a file and return its base64 content"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File does not exist: {file_path}"}
            
            if not os.path.isfile(file_path):
                return {"error": f"Path is not a file: {file_path}"}
            
            # Get file info
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Check file size limit (50MB max for base64 transfer)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                return {"error": f"File too large for direct download: {file_size} bytes (max: {max_size})"}
            
            # Read file and encode to base64
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            base64_content = base64.b64encode(file_data).decode('utf-8')
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            return {
                "success": True,
                "message": f"📥 File '{os.path.basename(file_path)}' prepared for download",
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size": file_size,
                "mime_type": mime_type,
                "content": base64_content
            }
            
        except Exception as e:
            return {"error": f"Failed to download file: {str(e)}"}

    async def get_download_url(self, file_path: str, **kwargs):
        """Get a download URL for a file (for direct HTTP download)"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File does not exist: {file_path}"}
            
            if not os.path.isfile(file_path):
                return {"error": f"Path is not a file: {file_path}"}
            
            # Get file info
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Create URL-encoded path for the download endpoint
            import urllib.parse
            encoded_path = urllib.parse.quote(file_path, safe='')
            
            return {
                "success": True,
                "message": f"📥 Download URL generated for '{os.path.basename(file_path)}'",
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size": file_size,
                "mime_type": mime_type,
                "download_url": f"/api/files/download/{encoded_path}"
            }
            
        except Exception as e:
            return {"error": f"Failed to get download URL: {str(e)}"}

    async def upload_base64_file(self, filename: str, content: str, directory: str = ".", **kwargs):
        """Upload a base64 encoded file to the server"""
        try:
            # Ensure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Decode base64 content
            try:
                file_data = base64.b64decode(content)
            except Exception as e:
                return {"error": f"Failed to decode base64 content: {str(e)}"}
            
            # Create the full file path
            file_path = os.path.join(directory, filename)
            
            # Check if file already exists and create unique name if needed
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(directory, new_filename)
                counter += 1
            
            # Write the file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Get file info
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "message": f"📤 Successfully uploaded '{os.path.basename(file_path)}' to '{directory}'",
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "directory": directory
            }
            
        except Exception as e:
            return {"error": f"Failed to upload file: {str(e)}"}

    async def upload_file(self, file_path: str, destination_directory: str = ".", **kwargs):
        """Upload/move a file to a destination directory"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"Source file does not exist: {file_path}"}
            
            # Ensure destination directory exists
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory, exist_ok=True)
            
            filename = os.path.basename(file_path)
            destination_path = os.path.join(destination_directory, filename)
            
            # Check if file already exists and create unique name if needed
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(destination_path):
                new_filename = f"{base_name}_{counter}{ext}"
                destination_path = os.path.join(destination_directory, new_filename)
                counter += 1
            
            # Copy the file
            shutil.copy2(file_path, destination_path)
            
            # Get file info
            stat = os.stat(destination_path)
            
            return {
                "success": True,
                "message": f"📤 Successfully uploaded '{os.path.basename(destination_path)}' to '{destination_directory}'",
                "filename": os.path.basename(destination_path),
                "path": destination_path,
                "size": stat.st_size,
                "directory": destination_directory
            }
            
        except Exception as e:
            return {"error": f"Failed to upload file: {str(e)}"}

    async def move_file(self, source: str, destination: str, **kwargs):
        """Move a file or directory from source to destination"""
        try:
            if not os.path.exists(source):
                return {"error": f"Source path does not exist: {source}"}
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            return {
                "success": True,
                "message": f"📂 Moved '{source}' to '{destination}'",
                "source": source,
                "destination": destination
            }
        except Exception as e:
            return {"error": f"Failed to move file: {str(e)}"}

    async def copy_file(self, source: str, destination: str, **kwargs):
        """Copy a file or directory from source to destination"""
        try:
            if not os.path.exists(source):
                return {"error": f"Source path does not exist: {source}"}
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            return {
                "success": True,
                "message": f"📋 Copied '{source}' to '{destination}'",
                "source": source,
                "destination": destination
            }
        except Exception as e:
            return {"error": f"Failed to copy file: {str(e)}"}

    async def rename_file(self, old_name: str, new_name: str, **kwargs):
        """Rename a file or directory"""
        try:
            if not os.path.exists(old_name):
                return {"error": f"File does not exist: {old_name}"}
            
            # If new_name is just a filename, use the same directory as old_name
            if not os.path.dirname(new_name):
                directory = os.path.dirname(old_name)
                new_name = os.path.join(directory, new_name)
            
            os.rename(old_name, new_name)
            return {
                "success": True,
                "message": f"🔄 Renamed '{old_name}' to '{new_name}'",
                "old_name": old_name,
                "new_name": new_name
            }
        except Exception as e:
            return {"error": f"Failed to rename file: {str(e)}"}

    async def bulk_rename(self, pattern: str = "", directory: str = ".", **kwargs):
        """Rename multiple files with a sequential pattern
        
        Args:
            pattern: Pattern description from AI (e.g., 'sequential pattern S2E25-S2E26-S2E27')
            directory: Target directory with files to rename
            **kwargs: Additional parameters including file paths
        """
        try:
            # Get file paths from kwargs
            file_paths = kwargs.get("file_paths", [])
            if not file_paths:
                return {"error": "No file paths provided for bulk rename"}
            
            # Get pattern from kwargs if not provided as positional arg
            if not pattern:
                pattern = kwargs.get("details", "")
            
            # Parse pattern to generate sequential names
            import re
            print(f"🔍 bulk_rename pattern: '{pattern}'")
            
            # Try to extract a proper S02E25-like pattern
            # Look for S##E## format
            season_episode_match = re.search(r'([Ss]?\d+[Ee]\d+)', pattern)
            if season_episode_match:
                # Found S02E25 format
                full_episode = season_episode_match.group(1)  # e.g., "S02E25"
                # Split pattern by this episode identifier
                parts = pattern.split(full_episode)
                base_pattern = parts[0]  # Everything before "S02E25"
                
                # Extract the episode number (the number after E or e)
                episode_num_match = re.search(r'[Ee](\d+)', full_episode)
                if episode_num_match:
                    start_num = int(episode_num_match.group(1))
                    # Reconstruct base with S##E format (keeping season number)
                    season_num_match = re.search(r'([Ss])(\d+)', full_episode)
                    if season_num_match:
                        season_prefix = season_num_match.group(1)  # "S" or "s"
                        season_num = season_num_match.group(2)     # "02"
                        # Add back S##E to base pattern
                        base_pattern = base_pattern + season_prefix + season_num + "E"
                    
                    # Strip "sequential pattern" prefix if present
                    base_pattern = re.sub(r'^[\s]*sequential\s+pattern[\s]*', '', base_pattern, flags=re.IGNORECASE).strip()
                    print(f"🔍 base_pattern: '{base_pattern}', start_num: {start_num}")
                else:
                    start_num = 1
                    base_pattern = ""
            else:
                # Fallback: use all numbers
                numbers = re.findall(r'\d+', pattern) if pattern else []
                print(f"🔍 bulk_rename numbers found: {numbers}")
                if numbers:
                    # Use the last number as the starting number for sequential naming
                    start_num = int(numbers[-1])
                    last_num_str = numbers[-1]
                    
                    # Extract base pattern (everything before the last number)
                    parts = pattern.rsplit(last_num_str, 1)  # Split from the right
                    base_pattern = parts[0] if parts else ""
                    print(f"🔍 base_pattern (fallback): '{base_pattern}', start_num: {start_num}")
                else:
                    start_num = 1
                    base_pattern = ""
            
            result_pattern = ""
            
            results = {"success": 0, "failed": 0, "renames": []}
            
            for idx, old_path in enumerate(file_paths):
                try:
                    if not os.path.exists(old_path):
                        results["failed"] += 1
                        results["renames"].append({"old": old_path, "new": None, "error": "File not found"})
                        continue
                    
                    # Generate new filename
                    new_num = start_num + idx
                    
                    # Preserve file extension
                    ext = os.path.splitext(old_path)[1]
                    
                    # Build new name
                    if base_pattern:
                        new_name = f"{base_pattern}{new_num}{ext}"
                    else:
                        new_name = f"file_{new_num}{ext}"
                    
                    # Get directory of old file
                    file_dir = os.path.dirname(old_path)
                    new_path = os.path.join(file_dir, new_name)
                    
                    # Rename
                    os.rename(old_path, new_path)
                    results["success"] += 1
                    results["renames"].append({"old": os.path.basename(old_path), "new": new_name, "success": True})
                    
                except Exception as e:
                    results["failed"] += 1
                    results["renames"].append({"old": old_path, "new": None, "error": str(e)})
            
            return {
                "success": True,
                "message": f"🔄 Renamed {results['success']} file(s)",
                "renamed": results["success"],
                "failed": results["failed"],
                "details": results["renames"]
            }
        except Exception as e:
            return {"error": f"Failed to bulk rename files: {str(e)}"}

    async def delete_file(self, path: str, force: bool = False, **kwargs):
        """Delete a file or directory"""
        try:
            if not os.path.exists(path):
                return {"error": f"Path does not exist: {path}"}
            
            # Safety check - don't delete system directories without force
            system_paths = ["/", "/usr", "/bin", "/etc", "/var", "/home"]
            if not force and any(path.startswith(sp) for sp in system_paths):
                return {"error": f"Refusing to delete system path without force flag: {path}"}
            
            if os.path.isdir(path):
                shutil.rmtree(path)
                return {
                    "success": True,
                    "message": f"🗑️ Deleted directory '{path}'",
                    "path": path,
                    "type": "directory"
                }
            else:
                os.remove(path)
                return {
                    "success": True,
                    "message": f"🗑️ Deleted file '{path}'",
                    "path": path,
                    "type": "file"
                }
        except Exception as e:
            return {"error": f"Failed to delete: {str(e)}"}

    async def create_directory(self, path: str, parents: bool = True, **kwargs):
        """Create a new directory"""
        try:
            if os.path.exists(path):
                return {"warning": f"Directory already exists: {path}"}
            
            os.makedirs(path, exist_ok=parents)
            return {
                "success": True,
                "message": f"📁 Created directory '{path}'",
                "path": path
            }
        except Exception as e:
            return {"error": f"Failed to create directory: {str(e)}"}

    async def list_files(self, directory: str = ".", pattern: str = "*", show_hidden: bool = False, **kwargs):
        """List files in a directory"""
        try:
            if not os.path.exists(directory):
                return {"error": f"Directory does not exist: {directory}"}
            
            if not os.path.isdir(directory):
                return {"error": f"Path is not a directory: {directory}"}
            
            files = []
            for item in glob.glob(os.path.join(directory, pattern)):
                if not show_hidden and os.path.basename(item).startswith('.'):
                    continue
                
                stat = os.stat(item)
                files.append({
                    "name": os.path.basename(item),
                    "path": item,
                    "type": "directory" if os.path.isdir(item) else "file",
                    "size": stat.st_size if os.path.isfile(item) else None,
                    "modified": stat.st_mtime
                })
            
            # Sort by name
            files.sort(key=lambda x: x["name"].lower())
            
            return {
                "success": True,
                "message": f"📂 Found {len(files)} items in '{directory}'",
                "directory": directory,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}

    async def find_files(self, pattern: str, directory: str = ".", recursive: bool = False, **kwargs):
        """Find files matching a pattern"""
        try:
            if not os.path.exists(directory):
                return {"error": f"Directory does not exist: {directory}"}
            
            matches = []
            if recursive:
                search_pattern = os.path.join(directory, "**", pattern)
                found = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(directory, pattern)
                found = glob.glob(search_pattern)
            
            for item in found:
                if os.path.exists(item):
                    stat = os.stat(item)
                    matches.append({
                        "name": os.path.basename(item),
                        "path": item,
                        "type": "directory" if os.path.isdir(item) else "file",
                        "size": stat.st_size if os.path.isfile(item) else None,
                        "modified": stat.st_mtime
                    })
            
            return {
                "success": True,
                "message": f"🔍 Found {len(matches)} matches for '{pattern}'",
                "pattern": pattern,
                "directory": directory,
                "recursive": recursive,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"error": f"Failed to find files: {str(e)}"}

    async def search_files(self, query: str, location_hint: str = None, **kwargs):
        """Search for files or folders by name with optional location hints
        
        Args:
            query: The search query (e.g., "vampire diaries", "vampire diaries folder")
            location_hint: Optional location hint (e.g., "desktop", "/Volumes/zai/Desktop")
        """
        try:
            import re
            
            # Normalize query - remove common words like "folder", "file", "on", "the"
            normalized_query = re.sub(r'\b(folder|file|on|the|my|a|an)\b', '', query, flags=re.IGNORECASE).strip()
            
            # Determine search directories based on location hint
            search_directories = []
            
            if location_hint:
                location_lower = location_hint.lower()
                # Map common location hints to actual paths
                if "desktop" in location_lower:
                    # Try common desktop paths
                    desktop_paths = [
                        "/Users/zai/Desktop",
                        "/Volumes/zai/Desktop",
                        os.path.expanduser("~/Desktop"),
                        "/Desktop"
                    ]
                    for path in desktop_paths:
                        if os.path.exists(path):
                            search_directories.append(path)
                            break
                elif location_hint.startswith("/"):
                    # Direct path provided
                    if os.path.exists(location_hint):
                        search_directories.append(location_hint)
                else:
                    # Try to find the location hint as a directory name
                    for root_dir in ["/", "/Users", "/Volumes"]:
                        if os.path.exists(root_dir):
                            for item in os.listdir(root_dir):
                                item_path = os.path.join(root_dir, item)
                                if os.path.isdir(item_path) and location_hint.lower() in item.lower():
                                    search_directories.append(item_path)
            
            # If no location hint or no matches, search common locations
            if not search_directories:
                search_directories = [
                    "/",
                    "/Users",
                    "/Volumes",
                    os.path.expanduser("~/Desktop"),
                    os.path.expanduser("~/Downloads"),
                ]
                # Filter to only existing directories
                search_directories = [d for d in search_directories if os.path.exists(d)]
            
            matches = []
            query_lower = normalized_query.lower()
            
            # Search recursively in each directory
            for search_dir in search_directories:
                try:
                    for root, dirs, files in os.walk(search_dir):
                        # Limit depth to avoid searching entire system (max 10 levels)
                        depth = root[len(search_dir):].count(os.sep)
                        if depth > 10:
                            dirs[:] = []  # Don't recurse deeper
                            continue
                        
                        # Search in directories
                        for dir_name in dirs:
                            if query_lower in dir_name.lower():
                                dir_path = os.path.join(root, dir_name)
                                try:
                                    stat = os.stat(dir_path)
                                    matches.append({
                                        "name": dir_name,
                                        "path": dir_path,
                                        "type": "directory",
                                        "size": None,
                                        "modified": stat.st_mtime
                                    })
                                except (OSError, PermissionError):
                                    pass
                        
                        # Search in files
                        for file_name in files:
                            if query_lower in file_name.lower():
                                file_path = os.path.join(root, file_name)
                                try:
                                    stat = os.stat(file_path)
                                    matches.append({
                                        "name": file_name,
                                        "path": file_path,
                                        "type": "file",
                                        "size": stat.st_size,
                                        "modified": stat.st_mtime
                                    })
                                except (OSError, PermissionError):
                                    pass
                        
                        # Limit results to avoid too many matches
                        if len(matches) >= 50:
                            break
                    
                    if len(matches) >= 50:
                        break
                except (OSError, PermissionError) as e:
                    # Skip directories we can't access
                    continue
            
            # Sort by relevance (exact matches first, then by name similarity)
            def relevance_score(match):
                name_lower = match["name"].lower()
                score = 0
                if query_lower in name_lower:
                    # Exact substring match
                    if name_lower.startswith(query_lower):
                        score += 100  # Starts with query
                    elif name_lower == query_lower:
                        score += 200  # Exact match
                    else:
                        score += 50  # Contains query
                return -score  # Negative for descending sort
            
            matches.sort(key=relevance_score)
            
            # Limit to top 20 results
            matches = matches[:20]
            
            return {
                "success": True,
                "message": f"🔍 Found {len(matches)} matches for '{query}'",
                "query": query,
                "location_hint": location_hint,
                "matches": matches,
                "count": len(matches),
                "type": "file_search"
            }
        except Exception as e:
            return {"error": f"Failed to search files: {str(e)}"}

    async def get_file_info(self, path: str, **kwargs):
        """Get detailed information about a file or directory"""
        try:
            if not os.path.exists(path):
                return {"error": f"Path does not exist: {path}"}
            
            stat = os.stat(path)
            info = {
                "name": os.path.basename(path),
                "path": os.path.abspath(path),
                "type": "directory" if os.path.isdir(path) else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "permissions": oct(stat.st_mode)[-3:]
            }
            
            if os.path.isfile(path):
                info["extension"] = os.path.splitext(path)[1]
            elif os.path.isdir(path):
                # Count items in directory
                try:
                    items = os.listdir(path)
                    info["item_count"] = len(items)
                except PermissionError:
                    info["item_count"] = "Permission denied"
            
            return {
                "success": True,
                "message": f"📄 Info for '{path}'",
                "info": info
            }
        except Exception as e:
            return {"error": f"Failed to get file info: {str(e)}"}

    async def organize_files(self, directory: str, method: str = "type", create_subdirs: bool = True, **kwargs):
        """Organize files in a directory by type, date, or other criteria"""
        try:
            if not os.path.exists(directory):
                return {"error": f"Directory does not exist: {directory}"}
            
            if not os.path.isdir(directory):
                return {"error": f"Path is not a directory: {directory}"}
            
            organized = {"moved": [], "created_dirs": [], "errors": []}
            
            # Get all files in directory (not subdirectories)
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            
            for filename in files:
                file_path = os.path.join(directory, filename)
                
                try:
                    if method == "type":
                        # Organize by file extension
                        ext = os.path.splitext(filename)[1].lower()
                        if ext:
                            subdir = ext[1:]  # Remove the dot
                        else:
                            subdir = "no_extension"
                    
                    elif method == "date":
                        # Organize by modification date (YYYY-MM format)
                        import datetime
                        mtime = os.path.getmtime(file_path)
                        date = datetime.datetime.fromtimestamp(mtime)
                        subdir = date.strftime("%Y-%m")
                    
                    else:
                        organized["errors"].append(f"Unknown organization method: {method}")
                        continue
                    
                    # Create subdirectory if it doesn't exist
                    subdir_path = os.path.join(directory, subdir)
                    if not os.path.exists(subdir_path) and create_subdirs:
                        os.makedirs(subdir_path)
                        organized["created_dirs"].append(subdir)
                    
                    # Move file
                    new_path = os.path.join(subdir_path, filename)
                    if not os.path.exists(new_path):
                        shutil.move(file_path, new_path)
                        organized["moved"].append({
                            "file": filename,
                            "from": file_path,
                            "to": new_path,
                            "category": subdir
                        })
                    else:
                        organized["errors"].append(f"Destination already exists: {new_path}")
                
                except Exception as e:
                    organized["errors"].append(f"Error organizing {filename}: {str(e)}")
            
            return {
                "success": True,
                "message": f"📁 Organized {len(organized['moved'])} files by {method}",
                "method": method,
                "directory": directory,
                "results": organized
            }
        except Exception as e:
            return {"error": f"Failed to organize files: {str(e)}"}