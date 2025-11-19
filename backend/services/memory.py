from config.env import supabase
import httpx
import asyncio
import json
from datetime import datetime
from typing import Optional


def _tag_multi_part(metadata: Optional[dict], *, is_multi_part: bool,
                    base_name: Optional[str] = None, part_index: Optional[int] = None,
                    part_total: Optional[int] = None) -> dict:
    """Ensure every memory row carries explicit multi-part markers."""
    meta = dict(metadata or {})
    meta["is_multi_part"] = bool(is_multi_part)
    meta["multi_part_tag"] = "yes" if is_multi_part else "no"
    if is_multi_part:
        if base_name:
            meta["multi_part_base"] = base_name
        if part_index is not None:
            meta["multi_part_index"] = part_index
        if part_total is not None:
            meta["multi_part_total"] = part_total
    else:
        meta.pop("multi_part_base", None)
        meta.pop("multi_part_index", None)
        meta.pop("multi_part_total", None)
    return meta





# =======================================================
# 🧠 6. MEMORY & EMBEDDINGS - Theater Archive & Librarians
# =======================================================
# region

async def get_or_create_thread(user_id: str, thread_title: str = None):
    """
    Returns an existing thread for the user or creates a new one.
    """
    # Try to get an existing thread (e.g., the most recent)
    res = supabase.table("chat_threads")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    threads = getattr(res, "data", [])
    if threads:
        return threads[0]["id"]

    # If no thread exists, create one
    data = {
        "user_id": user_id,
        "title": thread_title or "New Chat Thread"
    }
    new_thread = supabase.table("chat_threads").insert(data).execute()
    return new_thread.data[0]["id"]

async def log_message_to_db(thread_id, role, content, metadata=None):
    embedding = await embed_text_ollama(content)
    
    print(f"🔍 About to store embedding type: {type(embedding)}")
    print(f"🔍 Embedding length: {len(embedding) if embedding else 'None'}")
    
    try:
        # Convert Python list to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # Use raw SQL to properly insert the vector
        result = supabase.rpc(
            'insert_chat_message_with_vector',
            {
                'p_thread_id': thread_id,
                'p_role': role,
                'p_content': content,
                'p_metadata': metadata or {},
                'p_embedding': embedding_str
            }
        ).execute()
        
        print(f"🔍 Vector inserted via RPC")
        return result
        
    except Exception as e:
        print("❌ Failed to log message to Supabase:", e)
        return None



async def add_memory(memory):
    embedding = await embed_text_ollama(memory["content"])
    metadata = _tag_multi_part(memory.get("metadata"), is_multi_part=False)
    memory_to_insert = {
        **memory,
        "embedding": embedding,
        "importance": int(memory.get("importance", 5)),
        "metadata": metadata
    }
    return supabase.table("memories").insert(memory_to_insert).execute()


async def log_token_usage(
    user_id: str,
    model_name: str,
    tokens_used: int,
    request_type: str = "total",
    thread_id: str = None
):
    """
    Logs GPT-4o token usage to Supabase token_usage table.
    """
    try:
        record = {
            "user_id": user_id,
            "model_name": model_name,
            "tokens_used": tokens_used,
            "request_type": request_type,
            "thread_id": thread_id,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("token_usage").insert(record).execute()
        print(f"✅ Logged {tokens_used} tokens for user {user_id} on model {model_name}")
    except Exception as e:
        print(f"❌ Failed to log token usage: {e}")

# region Memroy Ingestion


# endregion

async def embed_text_ollama(text: str, model: str = "nomic-embed-text"):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:11434/api/embed",
                json={"model": model, "input": [text]},
                timeout=30.0
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Add debug logging
            print(f"🔍 Ollama response type: {type(data.get('embeddings', []))}")
            print(f"🔍 First embedding type: {type(data.get('embeddings', [[]])[0])}")
            
            if "embeddings" in data and data["embeddings"]:
                embedding = data["embeddings"][0]
                print(f"🔍 Embedding length: {len(embedding)}")
                print(f"🔍 First 5 values: {embedding[:5]}")
                return embedding  # This should be a list/array
            else:
                print(f"❌ No embeddings returned: {data}")
                return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def get_thread_messages_for_context(thread_id: str, limit: int = 50):
    """Fetch messages for chat context WITHOUT embeddings"""
    try:
        print(f"🔍 Fetching messages for thread_id: {thread_id}")
        
        history_resp = supabase.table("chat_messages") \
            .select("id, thread_id, role, content, metadata, created_at") \
            .eq("thread_id", thread_id) \
            .order("created_at", desc=False) \
            .limit(limit) \
            .execute()

        print(f"🔍 Raw response data: {history_resp}")
        
        history_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in getattr(history_resp, "data", [])
        ]
        
        print(f"🔍 Found {len(history_messages)} history messages")
        return history_messages
        
    except Exception as e:
        print("❌ Supabase chat_messages fetch failed:", str(e))
        return []


def _coerce_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return None


def normalize_memory_record(record: dict) -> dict:
    """Return a shallow copy with parsed metadata + an _is_multi_part flag."""
    metadata = record.get("metadata")
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except Exception:
            metadata = {}
    elif metadata is None:
        metadata = {}

    normalized = dict(record)
    normalized["metadata"] = metadata

    # Accept tags from either metadata or direct columns (in case RPC emits aliases)
    flag = _coerce_to_bool(metadata.get("multi_part_tag"))
    if flag is None:
        flag = _coerce_to_bool(metadata.get("is_multi_part"))
    if flag is None:
        flag = _coerce_to_bool(record.get("multi_part_tag"))
    if flag is None:
        flag = _coerce_to_bool(record.get("is_multi_part"))

    # Fall back to legacy naming pattern so older chunks (without metadata) are still filtered
    if flag is None:
        name = (normalized.get("name") or "").lower()
        if " - part " in name:
            flag = True

    normalized["_is_multi_part"] = bool(flag)
    return normalized


def select_memories_for_context(records: list[dict], *, deep_memory: bool, limit: int = 15):
    """Normalize, prefer non multi-part when deep memory is off, and always return up to `limit`."""
    normalized = [normalize_memory_record(r) for r in records]
    normalized.sort(key=lambda m: m.get("similarity") or 0, reverse=True)

    if deep_memory:
        selected = normalized[:limit]
        usable = len(normalized)
    else:
        solo = [m for m in normalized if not m["_is_multi_part"]]
        selected = solo[:limit]
        usable = len(solo)

    return selected[:limit], len(normalized), usable


async def main():
    text = "Hello world, this is a test embedding."
    emb = await embed_text_ollama(text)
    if emb:
        print(f"Embedding length: {len(emb)}")
        print(f"First 10 numbers: {emb[:10]}")

if __name__ == "__main__":
    asyncio.run(main())

# endregion
