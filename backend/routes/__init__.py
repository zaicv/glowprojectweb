"""
Routes module - HTTP endpoint handlers
"""
from routes.chat import router as chat_router
from routes.superpowers import router as superpowers_router
from routes.streaming import router as streaming_router
from routes.memory import router as memory_router
from routes.consciousness import router as consciousness_router
from routes.finance import router as finance_router
from routes.knowledge_base import router as knowledge_base_router

__all__ = [
    "chat_router",
    "superpowers_router",
    "streaming_router",
    "memory_router",
    "consciousness_router",
    "finance_router",
    "knowledge_base_router",
]
