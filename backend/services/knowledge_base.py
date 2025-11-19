"""
📚 Knowledge Base Service
Handles evidence-based therapeutic knowledge retrieval and formatting
"""
from typing import List, Optional, Dict, Any
import httpx
import re

# Import from your existing config
from config import supabase, client as groq_client

async def embed_text_ollama(text: str, model: str = "nomic-embed-text"):
    """Generate embedding using Ollama (same as memories)"""
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
                embedding = data["embeddings"][0]
                print(f"🔍 KB Embedding length: {len(embedding)}")
                return embedding  # This is a list/array
            else:
                print(f"❌ No embeddings returned from Ollama: {data}")
                return None
    except Exception as e:
        print(f"❌ Ollama embedding error: {e}")
        return None


async def search_knowledge_base(
    query: str,
    category: Optional[str] = None,
    content_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 5,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search knowledge base using semantic similarity with Ollama embeddings
    
    Args:
        query: User's query to search for
        category: Filter by category (e.g., 'CBT', 'DBT', 'trauma-informed')
        content_type: Filter by type (e.g., 'therapy_modality', 'dsm5', 'crisis_resource')
        tags: Filter by tags
        limit: Number of results to return
        user_id: User ID for personalized results
    
    Returns:
        List of relevant knowledge base entries with similarity scores
    """
    try:
        # Generate embedding using Ollama (same as memories)
        query_embedding = await embed_text_ollama(query)
        
        if not query_embedding:
            print("⚠️ Failed to generate embedding, skipping knowledge base search")
            return []
        
        print(f"🔍 KB Search: Generated embedding with {len(query_embedding)} dimensions")
        
        # Call the RPC function (same pattern as match_memories)
        response = supabase.rpc(
            'match_knowledge_base',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,  # Lower threshold for better recall
                'match_count': limit * 2  # Get more, filter later
            }
        ).execute()
        
        # Get the data
        results = response.data if response.data else []
        
        print(f"🔍 KB search returned {len(results)} raw results")
        
        # Apply filters in Python (after similarity search)
        if category:
            results = [r for r in results if r.get('category') == category]
            print(f"🔍 After category filter: {len(results)} results")
        
        if content_type:
            results = [r for r in results if r.get('content_type') == content_type]
            print(f"🔍 After content_type filter: {len(results)} results")
        
        if tags:
            results = [r for r in results if any(tag in r.get('tags', []) for tag in tags)]
            print(f"🔍 After tags filter: {len(results)} results")
        
        if user_id:
            # Filter for user's own entries OR public entries
            results = [
                r for r in results 
                if r.get('user_id') == user_id or r.get('access_level') == 'public'
            ]
        else:
            # Only return public entries if no user_id specified
            results = [r for r in results if r.get('access_level') == 'public']
        
        print(f"🔍 After access filter: {len(results)} results")
        
        final_results = results[:limit]
        print(f"✅ Knowledge base search returning {len(final_results)} results")
        
        return final_results
        
    except Exception as e:
        print(f"❌ Knowledge base search error: {e}")
        import traceback
        traceback.print_exc()
        return []


async def get_knowledge_by_category(
    category: str,
    subcategory: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get all knowledge entries for a specific category"""
    try:
        query = supabase.table('knowledge_base')\
            .select('*')\
            .eq('category', category)\
            .eq('is_active', True)\
            .limit(limit)
        
        if subcategory:
            query = query.eq('subcategory', subcategory)
        
        response = query.execute()
        return response.data if response.data else []
        
    except Exception as e:
        print(f"❌ Error fetching knowledge by category: {e}")
        return []


async def get_crisis_resources() -> List[Dict[str, Any]]:
    """Get crisis intervention resources - PRIORITY"""
    try:
        response = supabase.table('knowledge_base')\
            .select('*')\
            .or_('category.eq.crisis-skills,tags.cs.{CRITICAL}')\
            .eq('is_active', True)\
            .execute()
        
        print(f"✅ Crisis resources retrieved: {len(response.data) if response.data else 0} entries")
        return response.data if response.data else []
        
    except Exception as e:
        print(f"❌ Error fetching crisis resources: {e}")
        import traceback
        traceback.print_exc()
        return []


async def summarize_knowledge_entry(entry: Dict[str, Any], target_length: int = 300) -> str:
    """
    Use AI to summarize a knowledge base entry while preserving exact numbers and key data.
    
    Args:
        entry: Knowledge base entry dict with title and content
        target_length: Target character length for summary
    
    Returns:
        Summarized content preserving all numbers and critical information
    """
    try:
        content = entry.get('content', '')
        title = entry.get('title', 'Untitled')
        
        # If content is already short enough, return as-is
        if len(content) <= target_length:
            return content
        
        # Extract all numbers, dates, percentages, etc. to preserve them
        numbers_pattern = r'\b\d+[.,]?\d*\s*(?:%|mg|ml|kg|years?|months?|days?|hours?|minutes?|seconds?|times?|x|patients?|participants?|studies?|sessions?|weeks?)\b'
        numbers_found = re.findall(numbers_pattern, content, re.IGNORECASE)
        
        # Create a preservation note for the AI
        preservation_note = ""
        if numbers_found:
            unique_numbers = list(set(numbers_found[:20]))  # Limit to avoid too long prompt
            preservation_note = f"\n\nCRITICAL: You MUST preserve these exact values in your summary: {', '.join(unique_numbers)}"
        
        # Build summarization prompt
        summarize_prompt = f"""Summarize the following knowledge base entry in approximately {target_length} characters. 

CRITICAL REQUIREMENTS:
1. Preserve ALL numbers, statistics, percentages, dates, and measurements EXACTLY as written
2. Maintain key concepts, methodologies, and evidence-based information
3. Keep important technical terms and proper nouns
4. Preserve the essential meaning and actionable information
5. Be concise but comprehensive

Title: {title}

Content to summarize:
{content[:2000]}  {preservation_note}

Provide a concise summary that preserves all numerical data and key information:"""

        # Use Groq for fast summarization
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a precise summarization assistant that preserves all numerical data and key information exactly."},
                {"role": "user", "content": summarize_prompt}
            ],
            temperature=0.3,  # Lower temperature for more precise summaries
            max_tokens=400
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Verify numbers were preserved (basic check)
        original_numbers = set(re.findall(r'\b\d+[.,]?\d*\b', content))
        summary_numbers = set(re.findall(r'\b\d+[.,]?\d*\b', summary))
        
        # If we lost too many numbers, fall back to smart truncation
        if len(original_numbers) > 0 and len(summary_numbers) < len(original_numbers) * 0.7:
            print(f"⚠️ Summary may have lost numbers, using smart truncation for: {title}")
            return truncate_text_smart(content, target_length)
        
        print(f"✅ Summarized '{title}': {len(content)} → {len(summary)} chars")
        return summary
        
    except Exception as e:
        print(f"❌ Summarization error for '{entry.get('title', 'Unknown')}': {e}")
        # Fall back to smart truncation on error
        return truncate_text_smart(entry.get('content', ''), target_length)


def truncate_text_smart(text: str, max_chars: int) -> str:
    """
    Intelligently truncate text, preserving important parts.
    If text is very long, takes first portion and indicates truncation.
    """
    if len(text) <= max_chars:
        return text
    
    # For very long text, take the first portion (most relevant)
    # Reserve space for truncation indicator
    truncation_indicator = "\n[... content truncated for length ...]"
    available_chars = max_chars - len(truncation_indicator)
    
    # Try to break at sentence boundary if possible
    truncated = text[:available_chars]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    # Break at the last sentence or paragraph if within reasonable distance
    break_point = available_chars
    if last_period > available_chars * 0.8:
        break_point = last_period + 1
    elif last_newline > available_chars * 0.8:
        break_point = last_newline + 1
    
    return text[:break_point] + truncation_indicator


async def format_knowledge_for_context(
    knowledge_entries: List[Dict[str, Any]],
    max_tokens: int = 2000,  # Reduced default to be more conservative
    use_summarization: bool = True  # Enable AI summarization
) -> str:
    """
    Format knowledge base entries for inclusion in AI context with intelligent truncation.
    
    Args:
        knowledge_entries: List of knowledge base entries (should be sorted by relevance)
        max_tokens: Maximum tokens to include (rough estimate: 4 chars = 1 token)
    
    Returns:
        Formatted string for AI context
    """
    if not knowledge_entries:
        return ""
    
    # Reserve tokens for header and structure
    header = "=== RELEVANT KNOWLEDGE BASE INFORMATION ===\n"
    max_chars = max_tokens * 4  # Rough estimate: 4 chars per token
    reserved_chars = len(header) + 200  # Reserve for separators and metadata
    available_chars = max_chars - reserved_chars
    
    # Sort by similarity if available (higher = more relevant)
    sorted_entries = sorted(
        knowledge_entries,
        key=lambda x: x.get('similarity', 0),
        reverse=True
    )
    
    context_parts = [header]
    current_length = len(header)
    
    # Allocate tokens per entry based on relevance
    # Higher similarity entries get more tokens
    num_entries = len(sorted_entries)
    base_allocation = available_chars // max(num_entries, 1)
    max_per_entry = base_allocation * 2  # Cap individual entries
    
    for i, entry in enumerate(sorted_entries):
        similarity = entry.get('similarity', 0.5)
        
        # Allocate more tokens for higher similarity entries
        # Scale from 0.5x to 2x base allocation based on similarity
        similarity_multiplier = 0.5 + (similarity * 1.5)  # Range: 0.5 to 2.0
        entry_max_chars = min(
            int(base_allocation * similarity_multiplier),
            max_per_entry
        )
        
        # Build entry header
        entry_header = f"\n## {entry['title']}\n"
        
        if entry.get('category'):
            entry_header += f"Category: {entry['category']}"
            if entry.get('subcategory'):
                entry_header += f" > {entry['subcategory']}"
            entry_header += "\n"
        
        # Summarize or truncate content intelligently
        content = entry.get('content', '')
        header_length = len(entry_header) + 50  # Reserve for metadata
        content_max = max(entry_max_chars - header_length, 100)  # At least 100 chars
        
        # Use AI summarization if enabled and content is long enough to benefit
        if use_summarization and len(content) > content_max * 1.5:
            try:
                summarized_content = await summarize_knowledge_entry(entry, content_max)
                truncated_content = summarized_content
            except Exception as e:
                print(f"⚠️ Summarization failed, using truncation: {e}")
                truncated_content = truncate_text_smart(content, content_max)
        else:
            truncated_content = truncate_text_smart(content, content_max)
        
        entry_text = entry_header + f"\n{truncated_content}\n"
        
        # Add metadata if available
        if entry.get('metadata'):
            metadata = entry['metadata']
            metadata_text = ""
            if metadata.get('source'):
                metadata_text += f"\nSource: {metadata['source']}"
            if metadata.get('publication_year'):
                metadata_text += f" ({metadata['publication_year']})"
            if metadata.get('evidence_level'):
                metadata_text += f"\nEvidence Level: {metadata['evidence_level']}"
            if metadata_text:
                entry_text += metadata_text + "\n"
        
        entry_text += "\n---\n"
        
        # Check if adding this entry would exceed max tokens
        if current_length + len(entry_text) > max_chars:
            # Try to fit at least a summary
            remaining_chars = max_chars - current_length - 100
            if remaining_chars > 200:
                # Add a truncated version
                entry_text = entry_header + f"\n{truncate_text_smart(content, remaining_chars)}\n---\n"
                context_parts.append(entry_text)
            break
        
        context_parts.append(entry_text)
        current_length += len(entry_text)
    
    result = "".join(context_parts)
    estimated_tokens = len(result) // 4
    print(f"📚 Formatted knowledge context: {len(result)} chars (~{estimated_tokens} tokens), {len(context_parts)-1} entries")
    return result


async def test_knowledge_base():
    """Test knowledge base functionality"""
    try:
        print("\n🧪 Testing Knowledge Base...")
        
        # Test 1: Search for anxiety
        print("\n1️⃣ Testing search for 'anxiety'...")
        results = await search_knowledge_base("anxiety", limit=2)
        print(f"   Found {len(results)} results")
        if results:
            print(f"   First result: {results[0].get('title', 'No title')}")
        
        # Test 2: Get crisis resources
        print("\n2️⃣ Testing crisis resources...")
        crisis = await get_crisis_resources()
        print(f"   Found {len(crisis)} crisis resources")
        
        # Test 3: Format knowledge
        print("\n3️⃣ Testing formatting...")
        if results:
            formatted = await format_knowledge_for_context(results[:1], max_tokens=500, use_summarization=False)
            print(f"   Formatted length: {len(formatted)} chars")
        
        print("\n✅ Knowledge base tests complete!")
        
    except Exception as e:
        print(f"\n❌ Knowledge base test failed: {e}")
        import traceback
        traceback.print_exc()


# Export functions
__all__ = [
    'search_knowledge_base',
    'get_knowledge_by_category',
    'get_crisis_resources',
    'format_knowledge_for_context',
    'summarize_knowledge_entry',
    'test_knowledge_base'
]