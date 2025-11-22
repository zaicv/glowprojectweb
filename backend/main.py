# ============================================
# 🌟 The Glow Project API
# ============================================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import json

# ========== Config ==========
from config import logger

# ========== Services ==========
from services.websocket_manager import WebSocketManager
from services.chat import get_chat_response

# ========== Routes ==========
from routes import chat_router, streaming_router

# =======================================================
# 🎪 APP INITIALIZATION
# =======================================================

app = FastAPI(
    title="The Glow Project API",
    version="1.0",
    description="AI Chat API for The Glow Project Website"
)

# =======================================================
# 🦸 DEPENDENCIES
# =======================================================

websocket_manager = WebSocketManager()

# Inject websocket manager into routes
from routes.chat import set_websocket_manager
from routes.streaming import set_dependencies as set_streaming_dependencies

set_websocket_manager(websocket_manager)
set_streaming_dependencies({}, websocket_manager)  # Empty superpowers dict

print("✅ The Glow Project API initialized")

# =======================================================
# 🌐 MIDDLEWARE
# =======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =======================================================
# 🛣️ ROUTE REGISTRATION
# =======================================================

app.include_router(chat_router)
app.include_router(streaming_router)

print(f"✅ Routes registered: {len(app.routes)} total routes")

# =======================================================
# 🏠 HOME PAGE
# =======================================================

@app.get("/")
async def home():
    """API home page"""
        return {
        "name": "The Glow Project API",
        "version": "1.0",
        "status": "online",
        "endpoints": {
            "chat": "/api/chat",
            "streaming": "/api/chat/stream",
            "websocket": "/ws/{client_id}"
        }
    }

# =======================================================
# 🔌 WEBSOCKET ENDPOINT
# =======================================================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket connection for real-time chat updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "chat_message":
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

# =======================================================
# 🔍 UTILITY ENDPOINTS
# =======================================================

@app.options("/{full_path:path}")
async def options_catch_all(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "The Glow Project API"}

# =======================================================
# 🚀 SERVER START
# =======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
