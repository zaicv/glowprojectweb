# ============================================
# 📦 Pydantic Models/Schemas
# ============================================
# All BaseModel classes for request/response validation

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# =========================
# Chat Models
# =========================

class ChatInput(BaseModel):
    """Input model for chat endpoints"""
    message: str


class Message(BaseModel):
    """Generic message model"""
    message: str


# =========================
# Todo Parser Models
# =========================

class TodoParseRequest(BaseModel):
    """Request model for todo parsing with Mistral"""
    user_input: str


# =========================
# Memory Models
# =========================

class MemoryAddRequest(BaseModel):
    """Request model for adding memories"""
    content: str
    name: Optional[str] = None
    importance: Optional[int] = 5
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryRetrieveRequest(BaseModel):
    """Request model for retrieving memories"""
    query: str
    match_count: Optional[int] = 5


# =========================
# File Upload Models
# =========================

class FileUploadResponse(BaseModel):
    """Response model for file uploads"""
    success: bool
    message: str
    filename: str
    filepath: str
    size: int


# =========================
# Superpower Models
# =========================

class SuperpowerExecuteRequest(BaseModel):
    """Request model for executing superpower intents"""
    intent: str
    kwargs: Optional[Dict[str, Any]] = {}


class SuperpowerExecuteResponse(BaseModel):
    """Response model for superpower execution"""
    result: Any
    intent: str
    superpower: str


# =========================
# Streaming Models
# =========================

class YouTubeDownloadRequest(BaseModel):
    """Request model for YouTube downloads with WebSocket streaming"""
    url: str
    format: str = "mp4"
    client_id: str
    session_id: str
    custom_filename: Optional[str] = None
    output_directory: Optional[str] = None
    quality: Optional[str] = None


class RipDiscRequest(BaseModel):
    """Request model for disc ripping with WebSocket streaming"""
    mode: str = "full_rip"
    client_id: str
    session_id: str
    drive_path: Optional[str] = None


class StreamingResponse(BaseModel):
    """Generic response for streaming operations"""
    status: str
    session_id: str
    message: str


# =========================
# WebSocket Models
# =========================

class WebSocketMessage(BaseModel):
    """Generic WebSocket message model"""
    type: str
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ProgressUpdate(BaseModel):
    """Progress update model for WebSocket streaming"""
    progress: int  # 0-100
    status: str  # "initializing", "downloading", "complete", "error"
    message: str
    filename: Optional[str] = None
    speed: Optional[str] = None
    eta: Optional[str] = None


# =========================
# Command Parser Models
# =========================

class CommandParseRequest(BaseModel):
    """Request model for command parsing"""
    input: str


class CommandParseResponse(BaseModel):
    """Response model for command parsing"""
    parsed: str


# =========================
# Manual Metadata Models
# =========================

class ManualMetadataRequest(BaseModel):
    """Request model for manual metadata"""
    filename: str
    title: str


# =========================
# Speech/TTS Models
# =========================

class SpeakRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str


# =========================
# Generic API Response Models
# =========================

class SuccessResponse(BaseModel):
    """Generic success response"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    details: Optional[str] = None