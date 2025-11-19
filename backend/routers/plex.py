from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import httpx
import xml.etree.ElementTree as ET
import os
from superpowers.Plex import main as core

router = APIRouter(prefix="/plex", tags=["Plex Tools"])

@router.get("/libraries")
async def get_libraries():
    libraries = await core.fetch_libraries()
    return {"libraries": libraries}

@router.get("/library/{key}")
async def get_library_items(key: str):
    items = await core.fetch_library_items(key)
    return {"items": items}

@router.post("/scan/{key}")
async def scan_library(key: str):
    success = await core.trigger_scan(key)
    return {"status": "scan triggered" if success else "failed"}

@router.post("/rename/{rating_key}")
async def rename_item(rating_key: str, new_name: str = Form(...)):
    # Placeholder until rename logic added
    return {"status": f"Rename requested for {rating_key} -> {new_name}"}