# ============================================
# 🌊 Streaming Routes (WebSocket Progress)
# ============================================
# WebSocket-based endpoints for streaming progress updates during long operations

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio

router = APIRouter(prefix="/api/superpowers", tags=["streaming"])

# These will be injected from main.py
SUPERPOWERS: Dict[str, Any] = {}
websocket_manager = None

def set_dependencies(superpowers_dict: Dict[str, Any], ws_manager):
    """Inject dependencies from main.py"""
    global SUPERPOWERS, websocket_manager
    SUPERPOWERS = superpowers_dict
    websocket_manager = ws_manager
    print(f"✅ Streaming routes initialized")


# =========================
# YouTube Streaming Downloads
# =========================

@router.post("/youtube/stream-download")
async def stream_youtube_download(request: Request):
    """YouTube download with WebSocket progress streaming"""
    try:
        data = await request.json()
        url = data.get("url")
        format_type = data.get("format", "mp4")
        client_id = data.get("client_id")
        session_id = data.get("session_id")
        custom_filename = data.get("custom_filename")
        output_directory = data.get("output_directory")
        quality = data.get("quality", "1080" if format_type == "mp4" else "192")
        
        if not all([url, client_id, session_id]):
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required fields: url, client_id, session_id"}
            )
        
        # Register the download session
        websocket_manager.register_download_session(session_id, client_id)
        
        # Start download in background
        asyncio.create_task(
            download_with_progress_streaming_enhanced(
                url, format_type, session_id, client_id, 
                custom_filename, output_directory, quality
            )
        )
        
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Download started, progress will be streamed via WebSocket"
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/youtube/stream-download-fallback")
async def stream_youtube_download_fallback(request: Request):
    """YouTube download with fallback methods for problematic videos"""
    try:
        data = await request.json()
        url = data.get("url")
        format_type = data.get("format", "mp4")
        client_id = data.get("client_id")
        session_id = data.get("session_id")
        
        if not all([url, client_id, session_id]):
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required fields: url, client_id, session_id"}
            )
        
        websocket_manager.register_download_session(session_id, client_id)
        
        asyncio.create_task(
            download_with_fallback_methods(url, format_type, session_id, client_id)
        )
        
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Download started with fallback methods"
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# =========================
# RipDisc Streaming Processing
# =========================

@router.post("/ripdisc/stream-rip")
async def stream_ripdisc_process(request: Request):
    """RipDisc processing with WebSocket progress streaming"""
    try:
        data = await request.json()
        mode = data.get("mode", "full_rip")
        client_id = data.get("client_id")
        session_id = data.get("session_id")
        drive_path = data.get("drive_path")
        
        if not all([client_id, session_id]):
            return JSONResponse(status_code=400, content={"error": "Missing required fields"})
        
        websocket_manager.register_download_session(session_id, client_id)
        
        asyncio.create_task(
            ripdisc_with_progress_streaming(mode, session_id, client_id, drive_path)
        )
        
        return {
            "status": "started",
            "session_id": session_id,
            "message": f"Disc {mode} started, progress will be streamed via WebSocket"
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# =========================
# Background Tasks
# =========================

async def download_with_progress_streaming_enhanced(
    url: str, format_type: str, session_id: str, client_id: str,
    custom_filename: str = None, output_directory: str = None, quality: str = None
):
    """Enhanced background task with custom filename and directory support"""
    try:
        async def progress_callback(progress_data):
            await websocket_manager.send_progress(session_id, progress_data)

        await progress_callback({
            "progress": 0,
            "status": "initializing",
            "message": "Starting download..."
        })
        
        youtube_power = SUPERPOWERS.get("youtube")
        if not youtube_power:
            await progress_callback({
                "progress": 0,
                "status": "error",
                "message": "YouTube superpower not available"
            })
            return
        
        intent = "download_audio" if format_type == "mp3" else "download_video"
        
        result = await youtube_power.run(
            intent, 
            url=url, 
            format=format_type,
            quality=quality or ("1080" if format_type == "mp4" else "192"),
            custom_filename=custom_filename,
            output_dir=output_directory,
            websocket_callback=progress_callback
        )
        
        if result.get("success"):
            print(f"✅ Download completed: {result.get('title')}")
        elif result.get("error"):
            await progress_callback({
                "progress": 0,
                "status": "error",
                "message": result.get("error")
            })
        
    except Exception as e:
        await websocket_manager.send_progress(session_id, {
            "progress": 0,
            "status": "error",
            "message": f"Download failed: {str(e)}"
        })


async def download_with_fallback_methods(url: str, format_type: str, session_id: str, client_id: str):
    """Try multiple download methods for problematic videos"""
    async def progress_callback(progress_data):
        await websocket_manager.send_progress(session_id, progress_data)

    try:
        await progress_callback({
            "progress": 0,
            "status": "initializing",
            "message": "Trying enhanced download methods..."
        })
        
        youtube_power = SUPERPOWERS.get("youtube")
        if not youtube_power:
            await progress_callback({
                "progress": 0,
                "status": "error",
                "message": "YouTube superpower not available"
            })
            return
        
        intent = "download_audio" if format_type == "mp3" else "download_video"
        
        result = await youtube_power.run(
            intent,
            url=url,
            format=format_type,
            quality="720" if format_type == "mp4" else "192",
            websocket_callback=progress_callback,
            fallback_mode=True
        )
        
        if result.get("success"):
            print(f"✅ Fallback download completed: {result.get('title')}")
        elif result.get("error"):
            await progress_callback({
                "progress": 0,
                "status": "error", 
                "message": f"All download methods failed: {result.get('error')}"
            })
            
    except Exception as e:
        await progress_callback({
            "progress": 0,
            "status": "error",
            "message": f"Fallback download failed: {str(e)}"
        })


async def ripdisc_with_progress_streaming(mode: str, session_id: str, client_id: str, drive_path: str = None):
    """Background task for disc ripping with WebSocket progress updates"""
    try:
        async def progress_callback(progress_data):
            await websocket_manager.send_progress(session_id, progress_data)

        ripdisc_power = SUPERPOWERS.get("ripdisc")
        if not ripdisc_power:
            await progress_callback({
                "progress": 0,
                "status": "error",
                "message": "RipDisc superpower not available"
            })
            return
        
        if mode == "full_rip":
            result = await ripdisc_power.run(
                "rip_disc",
                mode="full_rip",
                websocket_callback=progress_callback,
                session_id=session_id,
                drive_path=drive_path
            )
        else:
            result = await ripdisc_power.run(
                "post_process",
                mode="post_process",
                websocket_callback=progress_callback,
                session_id=session_id,
                drive_path=drive_path
            )
        
        if result.get("status") == "success":
            print(f"✅ Disc processing completed successfully")
        elif result.get("error"):
            await progress_callback({
                "progress": 0,
                "status": "error",
                "message": result.get("error")
            })
        
    except Exception as e:
        await websocket_manager.send_progress(session_id, {
            "progress": 0,
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        })