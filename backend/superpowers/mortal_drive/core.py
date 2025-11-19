# superpowers/mortal_drive/core.py

from fastapi import HTTPException, Request, Depends
from pathlib import Path
from typing import List
import os

ALLOWED_ROOTS = [
    Path("/"),  # Full filesystem access
    Path("/Volumes")  # External and mounted volumes
]

def safe_path(path: str) -> Path:
    try:
        full_path = Path(path).resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    for allowed_root in ALLOWED_ROOTS:
        if allowed_root in full_path.parents or allowed_root == full_path:
            return full_path

    raise HTTPException(status_code=403, detail="Access denied")

def list_directory(path: str = "/") -> dict:
    dir_path = safe_path(path)

    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    items = []
    for item in dir_path.iterdir():
        try:
            items.append({
                "name": item.name,
                "path": str(item),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None
            })
        except Exception:
            continue

    return {
        "path": str(dir_path),
        "items": sorted(items, key=lambda x: (not x["is_dir"], x["name"]))
    }

def list_volumes() -> List[dict]:
    volumes_path = Path("/Volumes")
    if not volumes_path.exists():
        return []
    return [
        {
            "name": vol.name,
            "path": str(vol),
            "is_dir": vol.is_dir()
        }
        for vol in volumes_path.iterdir()
    ]
