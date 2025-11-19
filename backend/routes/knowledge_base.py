# ============================================
# 📚 Knowledge Base Routes
# ============================================

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from services.knowledge_base import embed_text_ollama
from config import supabase, whisper_model
from utils.file_ingestion import extract_text_from_file, chunk_text
import os

router = APIRouter(prefix="/api", tags=["knowledge_base"])


async def ingest_file_to_knowledge_base(entry_meta: dict, supabase, embed_text_ollama, whisper_model):
    """
    Extract, chunk, embed, and insert knowledge base entries for any supported file type.
    Similar to ingest_file_to_memories but for knowledge_base table.
    Uses file_name, file_type, and file_path columns (like memories table).
    """
    file_path = entry_meta.get("file_path")
    file_type = entry_meta.get("file_type")
    file_name = entry_meta.get("file_name", "Unknown")
    title = entry_meta.get("title", file_name.rsplit('.', 1)[0] if file_name else "Untitled")

    # For files uploaded to Supabase storage, we need to download them first
    temp_file_path = None
    original_file_path = file_path
    if file_path and not file_path.startswith('/'):
        try:
            print(f"🔽 Downloading file from Supabase storage: {file_path}")
            response = supabase.storage.from_("file-stores").download(file_path)
            temp_file_path = f"/tmp/{file_name}"
            with open(temp_file_path, "wb") as f:
                f.write(response)
            file_path = temp_file_path
            print(f"✅ File downloaded to: {file_path}")
        except Exception as e:
            print(f"❌ Failed to download file from storage: {e}")
            raise ValueError(f"Could not download file {file_name} from storage")

    # Extract text from the file
    if file_path and file_type:
        print(f"🔍 Extracting text from {file_type} file: {file_name}")
        text = await extract_text_from_file(file_path, file_type, whisper_model)
    else:
        text = entry_meta.get("content", "")

    if not text.strip():
        raise ValueError(f"No text extracted from {file_name or 'entry'}")

    print(f"📝 Extracted {len(text)} characters, chunking into pieces...")
    chunks = chunk_text(text)
    results = []
    total_chunks = len(chunks)
    is_multi_part = total_chunks > 1

    # Build base metadata for multi-part tracking (similar to memories)
    base_metadata = entry_meta.get("metadata", {})
    if is_multi_part:
        base_metadata.update({
            "is_multi_part": True,
            "multi_part_tag": "yes",
            "multi_part_base": title,
            "multi_part_total": total_chunks,
        })
    else:
        base_metadata.update({
            "is_multi_part": False,
            "multi_part_tag": "no",
        })

    for i, chunk in enumerate(chunks):
        # For multi-part files, append part number to title
        chunk_title = f"{title} - Part {i+1}" if is_multi_part else title
        
        print(f"🧠 Creating embedding for chunk {i+1}/{len(chunks)}")
        embedding = await embed_text_ollama(chunk)
        
        if not embedding:
            print(f"⚠️ Failed to generate embedding for chunk {i+1}, skipping...")
            continue

        # Build chunk-specific metadata
        chunk_metadata = base_metadata.copy()
        if is_multi_part:
            chunk_metadata["multi_part_index"] = i + 1

        # Create knowledge base entry with file columns (like memories)
        entry_to_insert = {
            "title": chunk_title,
            "content": chunk,
            "category": entry_meta.get("category", "general"),
            "content_type": entry_meta.get("content_type", file_type or "text"),
            "tags": entry_meta.get("tags", []),
            "embedding": embedding,
            "is_active": entry_meta.get("is_active", True),
            "access_level": entry_meta.get("access_level", "public"),
            "metadata": chunk_metadata,
            "needs_embedding": False,
            # File columns (like memories table)
            "file_name": file_name if original_file_path else None,
            "file_type": file_type if original_file_path else None,
            "file_path": original_file_path if original_file_path else None,
        }

        res = supabase.table("knowledge_base").insert(entry_to_insert).execute()
        results.append(res)

    # Clean up temporary file if we created one
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            print(f"🗑️ Cleaned up temporary file: {temp_file_path}")
        except Exception as e:
            print(f"⚠️ Failed to clean up temp file: {e}")

    print(f"✅ Successfully created {len(results)} knowledge base entry/chunks from {file_name}")
    return results


@router.post("/add-knowledge-base")
async def api_add_knowledge_base(request: Request):
    """Add a new entry to the knowledge base"""
    try:
        entry = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    try:
        if entry.get("file_type") and entry.get("file_path"):
            # File upload - extract and process (may return multiple chunks)
            results = await ingest_file_to_knowledge_base(
                entry, supabase, embed_text_ollama, whisper_model
            )
            # Extract all inserted data from results
            all_data = []
            for res in results:
                if res.data:
                    if isinstance(res.data, list):
                        all_data.extend(res.data)
                    else:
                        all_data.append(res.data)
            return {"status": "success", "rows": len(all_data), "result": all_data}
        else:
            # Text entry - generate embedding and insert
            text = entry.get("content", "")
            if not text.strip():
                return JSONResponse(status_code=400, content={"error": "Content is required"})
            
            embedding = await embed_text_ollama(text)
            if not embedding:
                return JSONResponse(status_code=500, content={"error": "Failed to generate embedding"})
            
            entry_to_insert = {
                "title": entry.get("title", "Untitled"),
                "content": text,
                "category": entry.get("category", "general"),
                "content_type": entry.get("content_type", "text"),
                "tags": entry.get("tags", []),
                "embedding": embedding,
                "is_active": entry.get("is_active", True),
                "access_level": entry.get("access_level", "public"),
                "metadata": entry.get("metadata", {}),
            }
            
            result = supabase.table("knowledge_base").insert(entry_to_insert).execute()
            return {"status": "success", "rows": 1, "result": result.data}
    except Exception as e:
        print(f"❌ Knowledge base add error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/knowledge-base")
async def get_knowledge_base(request: Request):
    """Get all knowledge base entries"""
    try:
        response = supabase.table("knowledge_base")\
            .select("*")\
            .eq("is_active", True)\
            .order("created_at", ascending=False)\
            .execute()
        
        return {
            "status": "success",
            "entries": response.data if response.data else [],
            "count": len(response.data) if response.data else 0
        }
    except Exception as e:
        print(f"❌ Knowledge base get error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

