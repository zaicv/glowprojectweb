"""
Services module for GlowGPT
Business logic and processing functions
"""
from .intent_detection import detect_user_intent
from .todo_parser import parse_todo_with_mistral

__all__ = [
    "detect_user_intent",
    "parse_todo_with_mistral",
]