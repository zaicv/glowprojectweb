# ============================================
# 🧠 Memory Routes
# ============================================

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from services.memory import embed_text_ollama, add_memory, select_memories_for_context
from config import supabase, whisper_model
from utils.file_ingestion import ingest_file_to_memories

router = APIRouter(prefix="/api", tags=["memory"])


@router.post("/add-memory")
async def api_add_memory(request: Request):
    """Add a new memory to the system"""
    try:
        memory = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    try:
        if memory.get("file_type") and memory.get("file_path"):
            results = await ingest_file_to_memories(
                memory, supabase, embed_text_ollama, whisper_model
            )
            return {"status": "success", "rows": len(results)}
        else:
            result = await add_memory(memory)
            return {"status": "success", "rows": 1, "result": result.data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/retrieve-memories", response_class=JSONResponse)
async def retrieve_memories(request: Request):
    """Retrieve relevant memories for a given query"""
    try:
        data = await request.json()
        user_input = data.get("query", "").strip()
        deep_memory = bool(data.get("deepMemory", False))
        
        if not user_input:
            return JSONResponse(status_code=400, content={"error": "Query is required"})
        
        query_embedding = await embed_text_ollama(user_input)
        match_count = data.get("match_count")
        if not isinstance(match_count, int):
            match_count = 200 if not deep_memory else 60
        
        memory_resp = supabase.rpc(
            "match_memories",
            {"query_embedding": query_embedding, "match_count": match_count}
        ).execute()
        
        memories = getattr(memory_resp, "data", []) or []
        selected_memories, total_candidates, usable_candidates = select_memories_for_context(
            memories,
            deep_memory=deep_memory,
            limit=15
        )
        
        memory_data = [
            {
                "id": m.get("id", f"memory-{i}"),
                "name": m.get("name", "Unknown Memory"),
                "content": m.get("content", ""),
                "similarity": m.get("similarity", 0.0),
                "importance": m.get("importance", 5),
                "created_at": m.get("created_at", datetime.now().isoformat()),
                "metadata": m.get("metadata", {}),
                "is_multi_part": m.get("_is_multi_part", False)
            }
            for i, m in enumerate(selected_memories)
        ]
        
        return {
            "memories": memory_data,
            "query": user_input,
            "count": len(memory_data),
            "total_candidates": total_candidates,
            "usable_candidates": usable_candidates
        }
        
    except Exception as e:
        print(f"❌ Memory retrieval error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
