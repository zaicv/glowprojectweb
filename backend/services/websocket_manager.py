# ============================================
# 🌊 WebSocket Manager
# ============================================
# Manages WebSocket connections for real-time progress updates

from fastapi import WebSocket
from typing import Dict
import json


class WebSocketManager:
    """
    Manages WebSocket connections and message routing.
    
    Features:
    - Connect/disconnect clients
    - Register download sessions
    - Send progress updates to specific clients
    - Broadcast messages
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.download_sessions: Dict[str, str] = {}  # session_id -> websocket_id
        self.active_chat_tasks: Dict[str, any] = {}  # client_id -> asyncio task
        self.cancelled_chats: set = set()  # Track cancelled chats
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"🔌 WebSocket client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        print(f"🔌 WebSocket client {client_id} disconnected")
    
    async def send_progress(self, session_id: str, progress_data: dict):
        """
        Send progress update to specific download session.
        
        Args:
            session_id: The download/process session ID
            progress_data: Dictionary containing progress info
                - progress: 0-100 percentage
                - status: "initializing", "downloading", "complete", "error"
                - message: Human-readable message
        """
        if session_id in self.download_sessions:
            client_id = self.download_sessions[session_id]
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(
                        json.dumps({
                            "type": "download_progress",
                            "session_id": session_id,
                            "data": progress_data
                        })
                    )
                except Exception as e:
                    print(f"❌ Failed to send progress: {e}")
                    self.disconnect(client_id)
    
    async def send_message(self, client_id: str, message: dict):
        """
        Send any message to specific client.
        
        Args:
            client_id: The WebSocket client ID
            message: Dictionary to send as JSON
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                self.disconnect(client_id)
    
    async def send_chat_chunk(self, client_id: str, chunk: str, done: bool = False):
        """
        Send chat response chunk to client.
        
        Args:
            client_id: The WebSocket client ID
            chunk: Text chunk to send
            done: Whether this is the final chunk
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps({
                    "type": "chat_chunk",
                    "chunk": chunk,
                    "done": done
                }))
            except Exception as e:
                print(f"❌ Failed to send chat chunk: {e}")
                self.disconnect(client_id)
    
    async def send_chat_metadata(self, client_id: str, metadata: dict):
        """
        Send chat metadata (memories, KB sources, etc.) to client.
        
        Args:
            client_id: The WebSocket client ID
            metadata: Dictionary containing memories, knowledge_base, tool_result, etc.
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps({
                    "type": "chat_metadata",
                    **metadata
                }))
            except Exception as e:
                print(f"❌ Failed to send chat metadata: {e}")
                self.disconnect(client_id)
    
    def register_download_session(self, session_id: str, client_id: str):
        """
        Register a download/process session with a client.
        
        Args:
            session_id: Unique session identifier
            client_id: WebSocket client ID to receive updates
        """
        self.download_sessions[session_id] = client_id
        print(f"📝 Registered download session {session_id} for client {client_id}")
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Dictionary to send as JSON to all clients
        """
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Failed to broadcast to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def get_active_connections_count(self) -> int:
        """Get the number of active WebSocket connections"""
        return len(self.active_connections)
    
    def get_active_sessions_count(self) -> int:
        """Get the number of registered download sessions"""
        return len(self.download_sessions)