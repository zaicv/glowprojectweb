# glow_state.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SystemState(BaseModel):
    cpu_usage: float = 0.0         # 0–1
    ram_usage: float = 0.0         # 0–1
    disk_free_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_read_mb_per_sec: float = 0.0
    disk_write_mb_per_sec: float = 0.0
    network_status: str = "unknown"  # connected / offline / limited
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    network_sent_mb_per_sec: float = 0.0
    network_recv_mb_per_sec: float = 0.0
    uptime_seconds: int = 0
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None
    cpu_temp_c: Optional[float] = None
    running_apps: List[str] = Field(default_factory=list)
    active_ports: List[Dict[str, Any]] = Field(default_factory=list)


class RuntimeState(BaseModel):
    backend_running: bool = True
    ollama_running: bool = False
    plex_running: bool = False

    active_model: Optional[str] = None         # e.g. "llama3-70b"
    available_models: List[str] = Field(default_factory=list)
    persona: Optional[str] = None              # "Phoebe"
    voice_mode: bool = False

    superpowers_loaded: List[str] = Field(default_factory=list)
    tokens_today: int = 0


class DeviceState(BaseModel):
    frontmost_app: Optional[str] = None
    frontmost_window: Optional[str] = None
    selected_text: Optional[str] = None
    clipboard: Optional[str] = None

    disc_mounted: bool = False
    disc_path: Optional[str] = None

    downloads_recent: List[str] = Field(default_factory=list)
    recent_files: List[Dict[str, Any]] = Field(default_factory=list)
    screen_brightness: Optional[int] = None
    audio_output_volume: Optional[float] = None


class EnvironmentState(BaseModel):
    now: datetime = Field(default_factory=datetime.utcnow)
    timezone: str = "America/Chicago"
    # weather, etc later if you want


class MemoryState(BaseModel):
    last_ingested_file: Optional[str] = None
    last_memory_added: Optional[str] = None
    memory_count: int = 0


class TaskInfo(BaseModel):
    id: str
    type: str                   # "rip_disc", "embed_file", etc
    status: str                 # "pending", "running", "done", "error"
    progress: float = 0.0       # 0–1
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class TasksState(BaseModel):
    active: List[TaskInfo] = Field(default_factory=list)
    recent: List[TaskInfo] = Field(default_factory=list)


class NotificationsState(BaseModel):
    disc_inserted: bool = False
    disc_path: Optional[str] = None
    timestamp: Optional[str] = None


class GlowState(BaseModel):
    system: SystemState = Field(default_factory=SystemState)
    runtime: RuntimeState = Field(default_factory=RuntimeState)
    device: DeviceState = Field(default_factory=DeviceState)
    environment: EnvironmentState = Field(default_factory=EnvironmentState)
    memory: MemoryState = Field(default_factory=MemoryState)
    tasks: TasksState = Field(default_factory=TasksState)
    notifications: NotificationsState = Field(default_factory=NotificationsState)

    # For future custom fields
    extra: Dict[str, Any] = Field(default_factory=dict)




# glow_state.py (continued)
import threading

class GlowStateStore:
    def __init__(self):
        self._state = GlowState()
        self._lock = threading.Lock()

    def get_state(self) -> GlowState:
        # Return a copy so nobody mutates it accidentally
        with self._lock:
            return self._state.copy(deep=True)

    def update(self, **kwargs):
        """
        kwargs is like:
          system={...}, runtime={...}, device={...}
        We'll merge into existing.
        """
        with self._lock:
            current = self._state

            for key, value in kwargs.items():
                if hasattr(current, key):
                    sub = getattr(current, key)
                    if isinstance(value, dict):
                        # merge dict into submodel
                        updated = sub.copy(update=value)
                        setattr(current, key, updated)
                    else:
                        setattr(current, key, value)

            self._state = current

    def replace(self, new_state: GlowState):
        with self._lock:
            self._state = new_state

# Global instance
glow_state_store = GlowStateStore()