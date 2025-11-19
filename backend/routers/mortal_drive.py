# The Core/GlowGPT/routers/mortal_drive.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from superpowers.mortal_drive import core as file_core

router = APIRouter(prefix="/mortal-drive", tags=["File Manager"])

@router.get("/list")
async def list_directory(path: str = Query("/")):
    try:
        result = file_core.list_directory(path)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e

@router.get("/volumes")
async def get_volumes():
    try:
        result = file_core.list_volumes()
        return JSONResponse(content={"volumes": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))