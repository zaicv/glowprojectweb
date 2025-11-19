"""
Config module for GlowGPT
Exports all configuration and clients
"""
from .logging import logger
from .env import (
    client,
    claude,
    supabase,
    whisper_model,
    openai_client,  # Add this
    GROQ_API_KEY,
    CLAUDE_API_KEY,
    OPENAI_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
)

__all__ = [
    "logger",
    "client",
    "claude",
    "supabase",
    "whisper_model",
    "openai_client",  # Add this
    "GROQ_API_KEY",
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_KEY",
]