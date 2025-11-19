# ============================================
# 🌟 GlowGPT Assistant API
# ============================================

# =======================================================
# 🎭 1. IMPORTS - Backstage Tool Crates
# =======================================================
# region

from fastapi import FastAPI, Form, Request, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
import json
import asyncio
import urllib.parse
import mimetypes
import time
from typing import Dict

# ========== Config ==========
from config import logger

# ========== Services ==========
from services.superpower_loader import load_superpowers
from services.websocket_manager import WebSocketManager
from services.persona import log_to_memory, read_memory
from services.chat import get_chat_response
from services.memory import log_message_to_db
from services.todo_parser import parse_todo_with_mistral

# ========== Routes ==========
from routes import (
    chat_router,
    superpowers_router,
    streaming_router,
    memory_router,
    consciousness_router,
    finance_router,
    knowledge_base_router,
)
from routes import tasks as tasks_router
from routes.chat import set_superpowers
from routes.superpowers import set_superpowers as set_superpowers_route
from routes.streaming import set_dependencies as set_streaming_dependencies

# Import glow_state_routes with debugging
try:
    from routes import glow_state_routes
    print(f"✅ [GlowState] Successfully imported glow_state_routes module")
    print(f"✅ [GlowState] Router object: {glow_state_routes.router}")
    print(f"✅ [GlowState] Router routes: {[r.path for r in glow_state_routes.router.routes]}")
except Exception as e:
    print(f"❌ [GlowState] Failed to import glow_state_routes: {e}")
    import traceback
    traceback.print_exc()
    glow_state_routes = None


from watchers.watchers import system_watcher, runtime_watcher, device_watcher



# ========== Legacy Routers ==========
from routers.plex import router as plex_router
from routers.mortal_drive import router as mortal_drive_router

# ========== Models ==========
from models.schemas import TodoParseRequest

# endregion

# =======================================================
# 🎪 2. APP INITIALIZATION
# =======================================================
# region

app = FastAPI(
    title="GlowGPT API",
    version="2.0",
    description="AI Assistant with Superpowers"
)

# endregion

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(system_watcher())
    loop.create_task(runtime_watcher())
    loop.create_task(device_watcher())
    
    # Warm up router for instant routing
    from services.glow_router import _warm_router
    await _warm_router()





# =======================================================
# 🦸 3. LOAD SUPERPOWERS & DEPENDENCIES
# =======================================================
# region

SUPERPOWERS = load_superpowers()
websocket_manager = WebSocketManager()

# Inject superpowers into routes
set_superpowers(SUPERPOWERS)
set_superpowers_route(SUPERPOWERS)
set_streaming_dependencies(SUPERPOWERS, websocket_manager)
from routes.chat import set_websocket_manager
set_websocket_manager(websocket_manager)

print(f"✅ Loaded {len(SUPERPOWERS)} superpowers")

# endregion

# =======================================================
# 🌐 4. MIDDLEWARE
# =======================================================
# region

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# endregion

# =======================================================
# 📂 5. STATIC FILES
# =======================================================
# region

app.mount("/static", StaticFiles(directory="static"), name="static")

# endregion

# =======================================================
# 🛣️ 6. ROUTE REGISTRATION
# =======================================================
# region

# Register glow_state_routes with debugging
if glow_state_routes and hasattr(glow_state_routes, 'router'):
    try:
        print(f"🔧 [GlowState] Attempting to register router: {glow_state_routes.router}")
        print(f"🔧 [GlowState] Router prefix: {glow_state_routes.router.prefix}")
        print(f"🔧 [GlowState] Router routes before registration: {len(glow_state_routes.router.routes)}")
        app.include_router(glow_state_routes.router)
        print(f"✅ [GlowState] Successfully registered glow_state_routes.router")
        # Verify it was registered
        registered_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        glow_paths = [p for p in registered_paths if 'glow' in p.lower()]
        print(f"✅ [GlowState] Registered paths containing 'glow': {glow_paths}")
    except Exception as e:
        print(f"❌ [GlowState] Failed to register router: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ [GlowState] Router not available or invalid")

app.include_router(chat_router)
app.include_router(superpowers_router)
app.include_router(streaming_router)
app.include_router(memory_router)
app.include_router(consciousness_router)
app.include_router(finance_router)
app.include_router(knowledge_base_router)
app.include_router(plex_router)
app.include_router(mortal_drive_router)
app.include_router(tasks_router.router)

# Debug: Print all registered routes
print(f"\n📋 [Route Debug] Total routes registered: {len(app.routes)}")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  - {list(route.methods)} {route.path}")

# endregion

# =======================================================
# 🏠 7. HOME PAGE (Legacy UI)
# =======================================================
# region

@app.get("/", response_class=HTMLResponse)
async def home():
    """Legacy home page with chat interface"""
    memory = read_memory()
    chat_html = ""
    for timestamp, entry in memory:
        if entry.startswith("You:"):
            css_class = "user"
        else:
            css_class = "ai"
        chat_html += f"""
        <div class="message {css_class}">
            <div class="bubble">
                {entry}
                <div class="timestamp">{timestamp}</div>
            </div>
        </div>
        """

    return f"""
    <html>
        <head>
            <title>GlOs - Glow OS</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <style>
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Inter', sans-serif;
                    background-color: #ffffff;
                    color: #000;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }}
                .logo {{
                    text-align: center;
                    padding: 1rem 0;
                }}
                .logo img {{
                    height: 40px;
                    opacity: 0.9;
                }}
                .chat-container {{
                    flex: 1;
                    overflow-y: auto;
                    padding: 1rem;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }}
                .message {{
                    display: flex;
                }}
                .message.user {{
                    justify-content: flex-end;
                }}
                .bubble {{
                    background-color: #f0f0f0;
                    color: #000;
                    padding: 0.75rem 1rem;
                    border-radius: 12px;
                    max-width: 60%;
                    position: relative;
                }}
                .timestamp {{
                    font-size: 0.7rem;
                    color: #555;
                    margin-top: 0.25rem;
                }}
                form {{
                    display: flex;
                    padding: 1rem;
                    border-top: 1px solid #ddd;
                    background: #f9f9f9;
                }}
                input[type="text"] {{
                    flex: 1;
                    padding: 0.75rem 1rem;
                    font-size: 1rem;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    outline: none;
                    background-color: #fff;
                    color: #000;
                }}
                input[type="submit"] {{
                    margin-left: 1rem;
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                    padding: 0.75rem 1.25rem;
                    font-weight: 600;
                    cursor: pointer;
                }}
                input[type="submit"]:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="logo">
                <img src="/static/GlOs.png" alt="GlOs Logo">
            </div>
            <div class="chat-container">{chat_html}</div>
            <form method="post" action="/process-entry">
                <input type="text" name="entry" placeholder="Send a message to GlOs..." autocomplete="off" required />
                <input type="submit" value="Send" />
            </form>
        </body>
    </html>
    """

# endregion

# =======================================================
# 🔧 8. LEGACY ENDPOINTS (To be migrated)
# =======================================================
# region

@app.post("/process-entry", response_class=HTMLResponse)
async def process_home(entry: str = Form(...)):
    """Legacy home page form submission"""
    log_to_memory("user", entry)
    print("🚀 /process-entry endpoint hit")
    try:
        ai_response = get_chat_response(entry)
    except Exception as e:
        ai_response = f"Error from AI: {e}"
    
    log_to_memory("glos", ai_response)
    return await home()


@app.post("/process", response_class=HTMLResponse)
async def process_entry(entry: str = Form(...)):
    """Legacy process endpoint"""
    print("🔧 /process endpoint hit")
    log_to_memory("user", entry)
    reply = get_chat_response(entry)
    thread_id = "default"  # Default thread ID for legacy support
    await log_message_to_db(thread_id, "assistant", reply)
    return f"<p>{reply}</p>"


@app.post("/api/parse-todo")
async def api_parse_todo(request: TodoParseRequest):
    """Frontend call for parsing todos"""
    return await parse_todo_with_mistral(request)


@app.post("/rip/manual-metadata", response_class=JSONResponse)
async def manual_metadata_handler(data: dict = Body(...)):
    """Manual metadata handler for RipDisc"""
    filename = data.get("filename")
    title = data.get("title")

    if not filename or not title:
        return JSONResponse(status_code=400, content={"error": "filename and title are required"})

    try:
        # Import here to avoid circular dependency
        from routers.mortal_drive import process_manual_metadata
        result = await process_manual_metadata(filename, title)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# endregion

# =======================================================
# 🔍 9. UTILITY ENDPOINTS
# =======================================================
# region

@app.get("/logs", response_class=PlainTextResponse)
async def get_logs():
    """View application logs"""
    try:
        with open("glowgpt.log", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No log file found."


@app.options("/{full_path:path}")
async def options_catch_all(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}


@app.post("/api/upload", response_class=JSONResponse)
async def upload_file(file: UploadFile = File(...), filename: str = None):
    """Upload a file to temporary storage for processing"""
    try:
        # Use provided filename or fallback to uploaded filename
        target_filename = filename or file.filename
        
        # Create temporary upload directory
        upload_dir = "/tmp/glow_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filepath to avoid conflicts
        timestamp = int(time.time())
        name, ext = os.path.splitext(target_filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Save uploaded file
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"File uploaded successfully",
            "filename": target_filename,
            "filepath": filepath,
            "size": len(content)
        }
        
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to upload file: {str(e)}"}
        )

# endregion

# =======================================================
# 📥 10. FILE DOWNLOAD ENDPOINTS
# =======================================================
# region

@app.get("/downloads/{filename}")
async def serve_download_file(filename: str):
    """Serve downloaded files for direct download"""
    file_path = os.path.join("/Users/zai/Desktop/plex/Podcasts", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/api/files/download/{encoded_path:path}")
async def download_file_endpoint(encoded_path: str):
    """Download any file from the server using encoded path"""
    try:
        print(f"🔍 [DOWNLOAD DEBUG] Starting download process...")
        print(f"🔍 [DOWNLOAD DEBUG] Encoded path received: {encoded_path}")
        
        # Decode the file path
        file_path = urllib.parse.unquote(encoded_path)
        print(f"🔍 [DOWNLOAD DEBUG] Decoded file path: {file_path}")
        
        # Security check - ensure path exists and is a file
        if not os.path.exists(file_path):
            print(f"❌ [DOWNLOAD DEBUG] File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        print(f"✅ [DOWNLOAD DEBUG] File exists: {file_path}")
        
        if not os.path.isfile(file_path):
            print(f"❌ [DOWNLOAD DEBUG] Path is not a file: {file_path}")
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path}")
        
        print(f"✅ [DOWNLOAD DEBUG] Path is a valid file")
        
        # Additional security - prevent directory traversal attacks
        file_path = os.path.abspath(file_path)
        print(f"🔍 [DOWNLOAD DEBUG] Absolute file path: {file_path}")
        
        # Get file info
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        print(f"🔍 [DOWNLOAD DEBUG] Filename: {filename}")
        print(f"🔍 [DOWNLOAD DEBUG] File size: {file_size} bytes")
        
        # Get MIME type
        try:
            mime_type, encoding = mimetypes.guess_type(file_path)
            print(f"🔍 [DOWNLOAD DEBUG] MIME type detected: {mime_type}")
            print(f"🔍 [DOWNLOAD DEBUG] Encoding: {encoding}")
            
            if not mime_type:
                mime_type = 'application/octet-stream'
                print(f"🔍 [DOWNLOAD DEBUG] Using fallback MIME type: {mime_type}")
        except Exception as mime_error:
            print(f"❌ [DOWNLOAD DEBUG] MIME type detection failed: {str(mime_error)}")
            mime_type = 'application/octet-stream'
        
        print(f"✅ [DOWNLOAD DEBUG] Final MIME type: {mime_type}")
        print(f"✅ [DOWNLOAD DEBUG] Preparing FileResponse...")
        
        # Create response headers
        headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Content-Length": str(file_size)
        }
        print(f"🔍 [DOWNLOAD DEBUG] Response headers: {headers}")
        
        print(f"🚀 [DOWNLOAD DEBUG] Sending file: {filename} ({file_size} bytes, {mime_type})")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=mime_type,
            headers=headers
        )
        
    except HTTPException as http_error:
        print(f"❌ [DOWNLOAD DEBUG] HTTP Exception: {http_error.detail}")
        raise
    except Exception as e:
        print(f"❌ [DOWNLOAD DEBUG] Unexpected error: {str(e)}")
        print(f"❌ [DOWNLOAD DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"❌ [DOWNLOAD DEBUG] Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/api/files/stream/{encoded_path:path}")
async def stream_file_endpoint(encoded_path: str):
    """Stream large files with support for range requests"""
    try:
        print(f"🔍 [STREAM DEBUG] Starting stream process...")
        print(f"🔍 [STREAM DEBUG] Encoded path received: {encoded_path}")
        
        # Decode the file path
        file_path = urllib.parse.unquote(encoded_path)
        print(f"🔍 [STREAM DEBUG] Decoded file path: {file_path}")
        
        # Security check - ensure path exists and is a file
        if not os.path.exists(file_path):
            print(f"❌ [STREAM DEBUG] File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            print(f"❌ [STREAM DEBUG] Path is not a file: {file_path}")
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path}")
        
        # Additional security - prevent directory traversal attacks
        file_path = os.path.abspath(file_path)
        print(f"🔍 [STREAM DEBUG] Absolute file path: {file_path}")
        
        # Get MIME type
        try:
            mime_type, encoding = mimetypes.guess_type(file_path)
            print(f"🔍 [STREAM DEBUG] MIME type detected: {mime_type}")
            
            # Handle MKV files specifically (browsers need proper MIME type)
            if file_path.lower().endswith('.mkv'):
                mime_type = 'video/x-matroska'
                print(f"🔍 [STREAM DEBUG] MKV file detected, using video/x-matroska")
            
            if not mime_type:
                mime_type = 'application/octet-stream'
        except Exception as mime_error:
            print(f"❌ [STREAM DEBUG] MIME type detection failed: {str(mime_error)}")
            mime_type = 'application/octet-stream'
        
        print(f"🚀 [STREAM DEBUG] Streaming file: {os.path.basename(file_path)} ({mime_type})")
        
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException as http_error:
        print(f"❌ [STREAM DEBUG] HTTP Exception: {http_error.detail}")
        raise
    except Exception as e:
        print(f"❌ [STREAM DEBUG] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")

# endregion

# =======================================================
# 🔌 11. WEBSOCKET ENDPOINT
# =======================================================
# region

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket connection for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "register_download":
                session_id = message.get("session_id")
                if session_id:
                    websocket_manager.register_download_session(session_id, client_id)
                    await websocket_manager.send_message(client_id, {
                        "type": "download_registered", 
                        "session_id": session_id
                    })
            elif message.get("type") == "chat_message":
                # Handle chat streaming request
                from routes.chat import chat_with_assistant_stream
                import asyncio
                task = asyncio.create_task(chat_with_assistant_stream(message.get("data", {}), client_id))
                # Store task for potential cancellation
                if not hasattr(websocket_manager, 'active_chat_tasks'):
                    websocket_manager.active_chat_tasks = {}
                websocket_manager.active_chat_tasks[client_id] = task
            elif message.get("type") == "cancel_chat":
                # Cancel ongoing chat stream
                if hasattr(websocket_manager, 'active_chat_tasks'):
                    task = websocket_manager.active_chat_tasks.get(client_id)
                    if task and not task.done():
                        # Mark as cancelled
                        if not hasattr(websocket_manager, 'cancelled_chats'):
                            websocket_manager.cancelled_chats = set()
                        websocket_manager.cancelled_chats.add(client_id)
                        task.cancel()
                        del websocket_manager.active_chat_tasks[client_id]
                        await websocket_manager.send_message(client_id, {
                            "type": "chat_cancelled",
                            "message": "Chat cancelled by user"
                        })
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        websocket_manager.disconnect(client_id)

# endregion

# =======================================================
# 🚀 12. SERVER START
# =======================================================
# region

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# endregion
