"""
🎬 Intent Detection - Assistant Directors
Uses Mistral to detect user intent and route to appropriate superpowers
"""
import json
import re
from typing import Dict, List
from ollama import chat as mistral_chat


def detect_user_intent(user_input: str, superpowers: dict) -> dict:
    """
    Detects user intent using Mistral LLM
    
    Args:
        user_input: Raw user message
        superpowers: Dictionary of loaded superpowers
        
    Returns:
        Dictionary with intent and extracted parameters
    """
    # Gather all available intents dynamically from superpowers
    dynamic_intents = []
    for power in superpowers.values():
        dynamic_intents.extend(power.intent_map.keys())

    # Add your global / built-in intents
    base_intents = ["chat", "download", "search", "code", "rip_disc", "manual_metadata", "unknown"]
    all_intents = base_intents + dynamic_intents

    # STEP 1: Pre-check for comma-separated movie titles (only for rip disc context)
    # Only trigger manual_metadata_bulk if it's clearly a metadata request
    if "," in user_input and "/title" not in user_input.lower() and "=" not in user_input:
        # Check if it looks like titles (no file operations keywords)
        file_ops_keywords = ["rename", "move", "copy", "delete", "organize", "sort", "reorder", "rename these", "change name"]
        if not any(keyword in user_input.lower() for keyword in file_ops_keywords):
            # Looks like metadata titles, not file operations
            return {
                "intent": "manual_metadata_bulk",
                "titles": [t.strip() for t in user_input.split(",") if t.strip()]
            }
    
    # STEP 2: Default fallback — use Mistral for other intent detection
    response = mistral_chat(
        model="mistral",
        messages=[
            {
                "role": "user",
                "content": f"""
You are an intent detection assistant. Analyze the input and return a JSON object with the following fields:

- "intent": one of {all_intents}
- "mode": for "rip_disc" intent, either "full_rip" or "post_process". Default to "full_rip" if unclear.
- "url": (if a URL is present in the message, else null)
- "details": optional string for any extra context
- "key": optional key or name of a specific Plex library (if relevant)
- "filename": (for "manual_metadata" only — the file needing metadata, like "Divergent.mkv")
- "title": (for "manual_metadata" only — the correct movie/show title, like "Divergent")
- "query": (for computational intents like compute, solve, calculate, convert, lookup, analyze, compare, explain)

Special handling:
If the user input starts with "/title", like:
    /title Divergent.mkv = Divergent
Then return:
    {{
      "intent": "manual_metadata",
      "filename": "Divergent.mkv",
      "title": "Divergent"
    }}

Examples:
- "Download this video: https://youtube.com/xyz" → intent: "download", url: "https://youtube.com/xyz"
- "Can you scan my TV shows?" → intent: "scan_plex"
- "What Plex libraries do I have?" → intent: "list_plex_libraries"
- "Show me everything in Documentaries" → intent: "list_plex_items", key: "Documentaries"
- "Rip the disc and add it to plex" → intent: "rip_disc", mode: "full_rip"
- "I already ripped the disc, just post process the files" → intent: "rip_disc", mode: "post_process"
- "/title Divergent.mkv = Divergent" → intent: "manual_metadata", filename: "Divergent.mkv", title: "Divergent"

**File Operations (file_ops superpower):**
- "rename these files to S2E25, S2E26, S2E27..." → intent: "bulk_rename", details: "sequential pattern S2E25-S2E26-S2E27"
- "move these to the Movies folder" → intent: "move_file", details: "target: Movies folder"
- "delete these selected files" → intent: "delete_file"
- "copy these files" → intent: "copy_file"
- "create a new folder called Downloads" → intent: "create_directory", details: "folder name: Downloads"
- "organize files by type" → intent: "organize_files", details: "by type"

**NEW: Plex Video Playback:**
- "play 42 from my plex server" → intent: "play_video", title: "42"
- "play Monster's Inc. from my plex server" → intent: "play_video", title: "Monster's Inc."
- "play Frozen from my plex server" → intent: "play_video", title: "Frozen"
- "stream The Matrix from plex" → intent: "stream_media", title: "The Matrix"
- "watch Inception on plex" → intent: "play_video", title: "Inception"

**NEW: Computational Queries (Wolfram Alpha):**
- "solve 2x + 5 = 13" → intent: "solve", query: "2x + 5 = 13"
- "compute the derivative of x^2 + 3x + 1" → intent: "compute", query: "derivative of x^2 + 3x + 1"
- "calculate 15% of 200" → intent: "calculate", query: "15% of 200"
- "convert 100 USD to EUR" → intent: "convert", query: "100 USD to EUR"
- "lookup population of Tokyo" → intent: "lookup", query: "population of Tokyo"
- "analyze y = mx + b" → intent: "analyze", query: "y = mx + b"
- "compare GDP of USA vs China" → intent: "compare", query: "GDP of USA vs China"
- "explain photosynthesis" → intent: "explain", query: "photosynthesis"

**NEW: Health Logs:**
- "log my weight as 150" → intent: "log_weight", details: "150"
- "what was my last weight" → intent: "get_last_weight"
- "show me my blood pressure history" → intent: "get_bp"

Input: {user_input}
"""
            }
        ]
    )

    try:
        return json.loads(response["message"]["content"])
    except Exception as e:
        return {"intent": "unknown", "error": str(e)}


__all__ = ["detect_user_intent"]