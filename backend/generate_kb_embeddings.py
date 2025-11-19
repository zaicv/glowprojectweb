"""
Generate Ollama embeddings for knowledge base entries
"""
import asyncio
import httpx
from config import supabase


async def generate_ollama_embedding(text: str, model: str = "nomic-embed-text"):
    """Generate embedding using Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:11434/api/embed",
                json={"model": model, "input": [text]},
                timeout=30.0
            )
            resp.raise_for_status()
            data = resp.json()
            if "embeddings" in data and data["embeddings"]:
                return data["embeddings"][0]
            return None
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None


async def generate_embeddings_for_knowledge_base():
    """Generate embeddings for all entries needing embedding or missing embeddings"""
    # Get all entries that either need embedding or have NULL embedding
    response = supabase.table('knowledge_base')\
        .select('id, title, content, embedding, needs_embedding')\
        .execute()

    entries = response.data
    print(f"📚 Found {len(entries)} entries in knowledge base")

    success_count = 0
    fail_count = 0

    for i, entry in enumerate(entries):
        try:
            # Skip if embedding exists and doesn't need update
            if entry.get("embedding") and not entry.get("needs_embedding", True):
                continue

            # Combine title and content
            text_to_embed = f"{entry['title']}\n\n{entry['content']}"

            # Generate embedding
            embedding = await generate_ollama_embedding(text_to_embed)
            if not embedding:
                print(f"❌ {i+1}/{len(entries)}: Failed to embed '{entry['title']}'")
                fail_count += 1
                continue

            # Decide update method
            if entry.get("embedding"):
                # ✅ Existing entry → update directly
                supabase.table("knowledge_base")\
                    .update({"embedding": embedding, "needs_embedding": False})\
                    .eq("id", entry["id"])\
                    .execute()
            else:
                # ✅ New entry → use RPC
                supabase.rpc(
                    'update_knowledge_base_embedding',
                    {
                        'kb_id': entry['id'],
                        'new_embedding': embedding
                    }
                ).execute()
                # Also mark as embedded
                supabase.table("knowledge_base")\
                    .update({"needs_embedding": False})\
                    .eq("id", entry["id"])\
                    .execute()

            success_count += 1
            print(f"✅ {i+1}/{len(entries)}: Embedded '{entry['title'][:50]}...'")
            await asyncio.sleep(0.2)

        except Exception as e:
            fail_count += 1
            print(f"❌ {i+1}/{len(entries)}: Error for '{entry['title']}': {e}")

    print(f"\n🎉 Finished!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📊 Total processed: {len(entries)}")


if __name__ == "__main__":
    print("🚀 Starting knowledge base embedding generation...")
    print("⚠️  Make sure Ollama is running: ollama serve")
    asyncio.run(generate_embeddings_for_knowledge_base())