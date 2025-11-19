# watchers.py
import asyncio
import psutil
import os
import subprocess
from datetime import datetime
from typing import Optional
from glowos.glow_state import glow_state_store
from services.superpower_loader import load_superpowers
from config import supabase


async def system_watcher():
    """CPU, RAM, disk, network, battery, apps, ports."""
    boot_time = psutil.boot_time()
    last_net_io = None
    last_disk_io = None
    await asyncio.sleep(1)  # Initial delay for first measurement
    
    while True:
        cpu = psutil.cpu_percent() / 100.0
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb_per_sec = 0.0
        disk_write_mb_per_sec = 0.0
        if last_disk_io is not None and disk_io:
            disk_read_mb_per_sec = (disk_io.read_bytes - last_disk_io.read_bytes) / (1024**2) / 5.0
            disk_write_mb_per_sec = (disk_io.write_bytes - last_disk_io.write_bytes) / (1024**2) / 5.0
        last_disk_io = disk_io
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_sent_mb_per_sec = 0.0
        network_recv_mb_per_sec = 0.0
        if last_net_io is not None and net_io:
            network_sent_mb_per_sec = (net_io.bytes_sent - last_net_io.bytes_sent) / (1024**2) / 5.0
            network_recv_mb_per_sec = (net_io.bytes_recv - last_net_io.bytes_recv) / (1024**2) / 5.0
        last_net_io = net_io
        
        uptime_seconds = int(datetime.now().timestamp() - boot_time)

        # Network status
        network_status = "unknown"
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1000', '8.8.8.8'],
                capture_output=True,
                timeout=2
            )
            network_status = "connected" if result.returncode == 0 else "offline"
        except:
            network_status = "unknown"
        
        # Battery
        battery_percent = None
        battery_plugged = None
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = battery.percent
                battery_plugged = battery.power_plugged
        except:
            pass
        
        # CPU temp (macOS - requires smcFanControl or similar)
        cpu_temp = None
        try:
            result = subprocess.run(
                ['osascript', '-e', 'do shell script "sudo powermetrics --samplers smc -n 1 -i 1000 | grep \"CPU die temperature\" | awk \'{print $4}\'"'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                cpu_temp = float(result.stdout.strip().replace('C', ''))
        except:
            pass
        
        # Running apps
        running_apps = []
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of every application process'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                apps = result.stdout.strip().split(', ')
                running_apps = [a.strip() for a in apps if a.strip()][:20]
        except:
            pass
        
        # Active ports
        active_ports = []
        try:
            connections = psutil.net_connections(kind='inet')
            ports = {}
            for conn in connections[:50]:
                if conn.status == 'LISTEN':
                    port = conn.laddr.port
                    if port not in ports:
                        ports[port] = {"port": port, "protocol": "tcp", "pid": conn.pid}
            active_ports = list(ports.values())[:10]
        except:
            pass
        
        glow_state_store.update(
            system={
                "cpu_usage": cpu,
                "ram_usage": ram.percent / 100.0,
                "disk_free_gb": round(disk.free / (1024**3), 1),
                "disk_used_gb": round(disk.used / (1024**3), 1),
                "disk_total_gb": round(disk.total / (1024**3), 1),
                "disk_read_mb_per_sec": round(disk_read_mb_per_sec, 2),
                "disk_write_mb_per_sec": round(disk_write_mb_per_sec, 2),
                "network_status": network_status,
                "network_sent_mb": round(net_io.bytes_sent / (1024**2), 1) if net_io else 0.0,
                "network_recv_mb": round(net_io.bytes_recv / (1024**2), 1) if net_io else 0.0,
                "network_sent_mb_per_sec": round(network_sent_mb_per_sec, 2),
                "network_recv_mb_per_sec": round(network_recv_mb_per_sec, 2),
                "uptime_seconds": uptime_seconds,
                "battery_percent": battery_percent,
                "battery_plugged": battery_plugged,
                "cpu_temp_c": cpu_temp,
                "running_apps": running_apps,
                "active_ports": active_ports,
            },
            environment={
                "now": datetime.utcnow(),
            },
        )
        await asyncio.sleep(5)


async def runtime_watcher():
    """Check Ollama, Plex, active model, superpowers, etc."""
    while True:
        # Example checks – you wire these into your real systems
        ollama_running = _check_process("ollama")
        plex_running = _check_process("Plex Media Server")

        # Pull from your config/persona system if you store it there
        current_model = _get_active_model_from_config()
        persona_name = _get_persona_name()

        superpowers = _get_loaded_superpowers_list()

        glow_state_store.update(
            runtime={
                "ollama_running": ollama_running,
                "plex_running": plex_running,
                "active_model": current_model,
                "persona": persona_name,
                "superpowers_loaded": superpowers,
            }
        )
        await asyncio.sleep(10)


def _check_process(name: str) -> bool:
    for p in psutil.process_iter(attrs=["name"]):
        if p.info["name"] and name.lower() in p.info["name"].lower():
            return True
    return False


def _get_active_model_from_config() -> Optional[str]:
    """Get the most recently used model from chat messages metadata."""
    try:
        # First try to get from most recent message metadata
        result = supabase.table("chat_messages")\
            .select("metadata")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        
        if result.data:
            for msg in result.data:
                metadata = msg.get("metadata")
                if metadata and isinstance(metadata, dict):
                    model = metadata.get("model")
                    if model:
                        model_map = {
                            "Groq": "llama-3.1-8b-instant",
                            "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
                            "Claude": "claude-3.5-sonnet-20240620",
                            "GPT-4o": "gpt-4o-2024-11-20",
                        }
                        return model_map.get(model, model)
        
        # Fallback: check thread model
        thread_result = supabase.table("chat_threads")\
            .select("model")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if thread_result.data and len(thread_result.data) > 0:
            model = thread_result.data[0].get("model")
            if model:
                model_map = {
                    "Groq": "llama-3.1-8b-instant",
                    "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
                    "Claude": "claude-3.5-sonnet-20240620",
                    "GPT-4o": "gpt-4o-2024-11-20",
                }
                return model_map.get(model, model)
        return None
    except Exception as e:
        print(f"⚠️ Failed to get active model: {e}")
        return None


def _get_persona_name() -> Optional[str]:
    """Get the most recently used persona name from chat messages metadata."""
    try:
        # Try to get persona from most recent chat message metadata
        result = supabase.table("chat_messages")\
            .select("metadata")\
            .eq("role", "user")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            metadata = result.data[0].get("metadata")
            if metadata and isinstance(metadata, dict):
                persona_name = metadata.get("persona_name")
                if persona_name:
                    return persona_name
        
        # Fallback: check if there's a default persona in the persona table
        persona_result = supabase.table("persona")\
            .select("name")\
            .order("created_at", desc=False)\
            .limit(1)\
            .execute()
        
        if persona_result.data and len(persona_result.data) > 0:
            return persona_result.data[0].get("name")
        
        return None
    except Exception as e:
        print(f"⚠️ Failed to get persona name: {e}")
        return None


def _get_loaded_superpowers_list() -> list:
    """Get list of currently loaded superpower names."""
    try:
        superpowers = load_superpowers()
        return list(superpowers.keys())
    except Exception as e:
        print(f"⚠️ Failed to get loaded superpowers: {e}")
        return []


DOWNLOADS_DIR = os.path.expanduser("~/Downloads")

async def device_watcher():
    """Watch discs + basic downloads list + frontmost app."""
    last_downloads = set()

    while True:
        # Disc detection - specifically look for optical drives
        disc_mounted = False
        disc_path = None
        
        try:
            # Use system_profiler to find optical drives
            result = subprocess.run(
                ['system_profiler', 'SPDiscBurningDataType', '-json'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import json
                try:
                    data = json.loads(result.stdout)
                    optical_drives = data.get('SPDiscBurningDataType', [])
                    
                    # Look for Pioneer drives specifically
                    for drive in optical_drives:
                        drive_name = drive.get('_name', '')
                        if 'pioneer' in drive_name.lower():
                            # Check if disc is mounted by looking for disc-specific folders
                            volumes = os.listdir("/Volumes")
                            for vol in volumes:
                                vol_path = f"/Volumes/{vol}"
                                # Check for disc structures (BDMV for Blu-ray, VIDEO_TS for DVD)
                                if os.path.exists(os.path.join(vol_path, "BDMV")) or \
                                   os.path.exists(os.path.join(vol_path, "VIDEO_TS")):
                                    disc_mounted = True
                                    disc_path = vol_path
                                    break
                            
                            # Also try MakeMKV to confirm disc presence
                            if not disc_mounted:
                                try:
                                    mkv = subprocess.run(
                                        ["/Applications/MakeMKV.app/Contents/MacOS/makemkvcon", "info", "disc:0"],
                                        capture_output=True,
                                        text=True,
                                        timeout=5
                                    )
                                    if mkv.returncode == 0 and mkv.stdout:
                                        # Disc is present, find mount point - exclude external drives
                                        volumes = os.listdir("/Volumes")
                                        excluded = ("Macintosh HD", "PlexServer", "Time Machine", "Backups")
                                        for vol in volumes:
                                            if vol not in excluded and not vol.startswith("."):
                                                vol_path = f"/Volumes/{vol}"
                                                # Only count as disc if it has disc structure
                                                if os.path.exists(vol_path) and (
                                                    os.path.exists(os.path.join(vol_path, "BDMV")) or
                                                    os.path.exists(os.path.join(vol_path, "VIDEO_TS"))
                                                ):
                                                    disc_mounted = True
                                                    disc_path = vol_path
                                                    break
                                except:
                                    pass
                            break
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"⚠️ Disc detection error: {e}")
        
        # Track previous state for disc insertion detection
        prev_state = glow_state_store.get_state()
        prev_disc_mounted = prev_state.device.disc_mounted if prev_state else False
        
        glow_state_store.update(
            device={
                "disc_mounted": disc_mounted,
                "disc_path": disc_path,
            }
        )
        
        # Detect disc insertion (wasn't mounted before, now is)
        if disc_mounted and not prev_disc_mounted and disc_path:
            print(f"💿 Disc inserted: {disc_path}")
            # Store notification flag for frontend to check
            glow_state_store.update(
                notifications={
                    "disc_inserted": True,
                    "disc_path": disc_path,
                    "timestamp": datetime.now().isoformat()
                }
            )

        # Simple downloads watcher (just keep names)
        if os.path.exists(DOWNLOADS_DIR):
            files = sorted(
                os.listdir(DOWNLOADS_DIR),
                key=lambda f: os.path.getmtime(os.path.join(DOWNLOADS_DIR, f)),
                reverse=True,
            )[:10]  # last 10
            glow_state_store.update(
                device={"downloads_recent": files}
            )
        
        # Frontmost app and window (macOS)
        frontmost_app = None
        frontmost_window = None
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
                capture_output=True,
                text=True,
                timeout=2
            )
            frontmost_app = result.stdout.strip() if result.returncode == 0 else None
            
            if frontmost_app:
                try:
                    window_result = subprocess.run(
                        ['osascript', '-e', f'tell application "{frontmost_app}" to get name of window 1'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    frontmost_window = window_result.stdout.strip() if window_result.returncode == 0 else None
                except:
                    pass
        except:
            pass
        
        # Recent files (last 5 accessed files in common dirs)
        recent_files = []
        try:
            common_dirs = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
            ]
            all_files = []
            for dir_path in common_dirs:
                if os.path.exists(dir_path):
                    try:
                        for f in os.listdir(dir_path)[:10]:
                            fpath = os.path.join(dir_path, f)
                            if os.path.isfile(fpath):
                                all_files.append({
                                    "name": f,
                                    "path": fpath,
                                    "modified": os.path.getmtime(fpath)
                                })
                    except:
                        pass
            recent_files = sorted(all_files, key=lambda x: x["modified"], reverse=True)[:5]
        except:
            pass
        
        # Screen brightness (macOS)
        screen_brightness = None
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to tell application process "SystemUIServer" to get value of slider 1 of group 1 of window 1'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                brightness = float(result.stdout.strip()) * 100
                screen_brightness = int(brightness)
        except:
            pass
        
        # Audio volume (macOS)
        audio_volume = None
        try:
            result = subprocess.run(
                ['osascript', '-e', 'output volume of (get volume settings)'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                audio_volume = float(result.stdout.strip()) / 100.0
        except:
            pass
        
        glow_state_store.update(device={
            "frontmost_app": frontmost_app,
            "frontmost_window": frontmost_window,
            "recent_files": recent_files,
            "screen_brightness": screen_brightness,
            "audio_output_volume": audio_volume,
        })

        await asyncio.sleep(7)