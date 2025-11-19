"""
📄 File Ingestion - Document Processing & Memory Creation
Extracts text from various file types and creates memory embeddings
"""
import os
import json
from typing import Optional
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import docx
import pytesseract
from PIL import Image

# Note: whisper_model and supabase will be passed as parameters


CHUNK_SIZE = 800  # adjust to control chunk size


def _tag_multi_part_metadata(metadata, *, is_multi_part: bool,
                             base_name: Optional[str] = None,
                             part_index: Optional[int] = None,
                             part_total: Optional[int] = None) -> dict:
    """Attach consistent multi-part markers so retrieval can filter reliably."""
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


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into smaller pieces for embeddings."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


async def extract_text_from_file(file_path: str, file_type: str, whisper_model) -> str:
    """
    Extracts readable text from various file types.
    
    Args:
        file_path: Path to the file
        file_type: MIME type of the file
        whisper_model: Whisper model instance for audio transcription
        
    Returns:
        Extracted text content
    """
    try:
        # ---- Plain Text / Markdown ----
        if file_type in ["text/plain", "text/markdown", "text/x-markdown"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        # ---- JSON ----
        elif file_type in ["application/json", "text/json"]:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)

        # ---- HTML ----
        elif file_type in ["text/html", "application/html"]:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            return soup.get_text(separator="\n", strip=True)

        # ---- PDF ----
        elif file_type == "application/pdf":
            reader = PdfReader(file_path)
            return "\n".join([p.extract_text() or "" for p in reader.pages])

        # ---- Word Docs ----
        elif file_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        # ---- Audio (MP3, WAV, etc.) ----
        elif file_type.startswith("audio/") or file_type.startswith("video/"):
            result = whisper_model.transcribe(file_path)
            return result["text"]

        # ---- Images ----
        elif file_type.startswith("image/"):
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)

        # ---- Fallback ----
        else:
            print(f"⚠️ Unsupported file type: {file_type}, treating as plain text")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                return ""
    
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        return ""


async def ingest_file_to_memories(memory_meta: dict, supabase, embed_text_ollama, whisper_model):
    """
    Extract, chunk, embed, and insert memory rows for any supported file type.
    
    Args:
        memory_meta: Dictionary with file metadata (file_path, file_type, file_name, etc.)
        supabase: Supabase client instance
        embed_text_ollama: Function to generate embeddings
        whisper_model: Whisper model for audio transcription
        
    Returns:
        List of insert results from Supabase
    """
    file_path = memory_meta["file_path"]
    file_type = memory_meta["file_type"]
    file_name = memory_meta["file_name"]
    custom_name = memory_meta.get("name", "").strip()  # Get custom name from user

    # For files uploaded to Supabase storage, we need to download them first
    temp_file_path = None
    if not file_path.startswith('/'):
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
    print(f"🔍 Extracting text from {file_type} file: {file_name}")
    text = await extract_text_from_file(file_path, file_type, whisper_model)
    
    if not text.strip():
        raise ValueError(f"No text extracted from {file_name}")

    print(f"📝 Extracted {len(text)} characters, chunking into pieces...")
    chunks = chunk_text(text)
    results = []
    total_chunks = len(chunks)
    is_multi_part = total_chunks > 1

    # Use custom name if provided, otherwise use filename without extension
    display_name = custom_name if custom_name else file_name.rsplit('.', 1)[0]

    for i, chunk in enumerate(chunks):
        # For the name field, use a consistent pattern that the frontend can group by
        name = f"{display_name} - Part {i+1}"
        print(f"🧠 Creating embedding for chunk {i+1}/{len(chunks)}")
        embedding = await embed_text_ollama(chunk)
        chunk_metadata = _tag_multi_part_metadata(
            memory_meta.get("metadata"),
            is_multi_part=is_multi_part,
            base_name=display_name,
            part_index=i + 1,
            part_total=total_chunks
        )
        memory_to_insert = {
            **memory_meta,
            "name": name,
            "content": chunk,
            "embedding": embedding,
            "importance": int(memory_meta.get("importance", 5)),
            "metadata": chunk_metadata,
        }
        res = supabase.table("memories").insert(memory_to_insert).execute()
        results.append(res)

    # Clean up temporary file if we created one
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            print(f"🗑️ Cleaned up temporary file: {temp_file_path}")
        except Exception as e:
            print(f"⚠️ Failed to clean up temp file: {e}")

    print(f"✅ Successfully created {len(results)} memory chunks from {file_name}")
    return results


__all__ = ["chunk_text", "extract_text_from_file", "ingest_file_to_memories", "CHUNK_SIZE"]
