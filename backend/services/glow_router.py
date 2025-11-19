"""
🚀 GlowRouter - Optimized for ChatGPT-level speed (<100ms)
Uses Groq + minimal RouterPacket + strict JSON output
"""
from typing import Dict, Optional, Any
from config import client as groq_client
import json
import asyncio
from datetime import datetime
import uuid
import time

SUPERPOWERS = None
_ROUTER_WARMED = False
_TOOL_CACHE = {}  # Cache tool lookups

# Core tools only (5-7 max for speed)
CORE_TOOLS = [
    "rip_disc",
    "download",
    "download_video", 
    "download_audio",
    "scan_plex",
    "search",
    "play_video",
    "file_ops",
    "search_files",
    "bulk_rename",
    "calculate",
    "compute",
    "solve"
]

# Comprehensive tool pattern matching (fast path)
TOOL_PATTERNS = {
    "scan_plex": ["scan plex", "scanning plex", "refresh plex", "update plex", "plex scan", "plex refresh"],
    "rip_disc": ["rip disc", "rip the disc", "rip dvd", "rip bluray", "rip blu-ray", "extract disc", "rip this"],
    "download": ["download", "youtube", "youtu.be", "youtube.com", "get video", "save video"],
    "download_video": ["download video", "get video", "save video"],
    "download_audio": ["download audio", "get audio", "save audio", "extract audio"],
    "search": ["search web", "web search", "google", "search for", "look up"],
    "search_files": ["look for", "find", "search for", "show me", "where is"],
    "calculate": ["calculate", "compute", "solve", "math", "what is", "how much"],
    "file_ops": ["rename", "move file", "organize files", "bulk rename", "rename files"],
    "play_video": ["play", "watch", "stream", "show me"],
}

def set_superpowers(superpowers: dict):
    global SUPERPOWERS, _TOOL_CACHE
    SUPERPOWERS = superpowers
    # Build tool cache for fast lookups
    _TOOL_CACHE = {}
    if superpowers:
        for power_name, power in superpowers.items():
            if hasattr(power, 'intent_map'):
                for intent in power.intent_map.keys():
                    if intent not in _TOOL_CACHE:
                        _TOOL_CACHE[intent] = power_name


async def _warm_router():
    """Warm up router on startup - prevents cold starts"""
    global _ROUTER_WARMED
    if _ROUTER_WARMED:
        return
    
    try:
        await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10,
            temperature=0
        )
        _ROUTER_WARMED = True
    except Exception:
        pass


def _truncate_message(message: str, max_tokens: int = 40) -> str:
    """Truncate user message to first ~40 tokens (ChatGPT pattern)"""
    words = message.split()
    if len(words) <= max_tokens:
        return message
    return " ".join(words[:max_tokens]) + "..."


def _filter_core_tools() -> list:
    """Return only core tools (5-7 max) for speed"""
    if not SUPERPOWERS:
        return []
    
    core_list = []
    seen_intents = set()
    
    for power_name, power in SUPERPOWERS.items():
        if hasattr(power, 'intent_map'):
            for intent, desc in power.intent_map.items():
                if intent in CORE_TOOLS and intent not in seen_intents:
                    core_list.append({
                        "name": intent,
                        "superpower": power.name,
                        "desc": desc[:60]
                    })
                    seen_intents.add(intent)
                    if len(core_list) >= 7:
                        break
        if len(core_list) >= 7:
            break
    
    return core_list


def _build_router_packet(user_message: str, glow_state: Any) -> Dict:
    """Build TINY RouterPacket (250-500 tokens max)"""
    truncated_msg = _truncate_message(user_message, max_tokens=40)
    
    state_snapshot = {
        "disc": glow_state.device.disc_mounted,
        "tasks": len([t for t in glow_state.tasks.active if t.status == "running"]) > 0
    }
    
    tools = _filter_core_tools()
    
    return {
        "msg": truncated_msg,
        "state": state_snapshot,
        "tools": tools
    }


async def _call_router_model(packet: Dict) -> Dict:
    """Call Groq with strict JSON schema - optimized for accuracy"""
    import re
    model_start = time.time()
    
    tools_text = "\n".join([
        f'{t["name"]}: {t["desc"]}'
        for t in packet["tools"]
    ])
    
    # Fast pattern matching first (handles 90% of cases)
    msg_lower = packet["msg"].lower().strip()
    
    for tool_name, patterns in TOOL_PATTERNS.items():
        if any(p in msg_lower for p in patterns):
            # Extract URL for download tools
            if tool_name in ("download", "download_video", "download_audio"):
                url_match = re.search(r'https?://[^\s]+', packet["msg"])
                if url_match:
                    return {
                        "mode": "tool",
                        "tool_name": tool_name,
                        "arguments": {"url": url_match.group(0)}
                    }
            # Extract query and location for file search
            elif tool_name == "search_files":
                # Extract the search query and location hint
                # Pattern: "look for X on desktop" or "find X folder"
                # First try to match with location hint
                query_match = re.search(r'(?:look for|find|search for|show me|where is)\s+(.+?)(?:\s+on\s+(?:my\s+)?(\w+))(?:\s+folder)?\s*$', msg_lower)
                if query_match:
                    query = query_match.group(1).strip()
                    location_hint = query_match.group(2) if query_match.group(2) else None
                else:
                    # Try without location hint
                    query_match = re.search(r'(?:look for|find|search for|show me|where is)\s+(.+?)(?:\s+folder)?\s*$', msg_lower)
                    if query_match:
                        query = query_match.group(1).strip()
                        location_hint = None
                    else:
                        # Fallback: extract everything after the pattern
                        query = None
                        for pattern in patterns:
                            if pattern in msg_lower:
                                idx = msg_lower.find(pattern)
                                query = packet["msg"][idx + len(pattern):].strip()
                                # Try to extract location hint - look for "on my X" or "on X"
                                location_match = re.search(r'\s+on\s+(?:my\s+)?(\w+)', query, re.IGNORECASE)
                                if location_match:
                                    location_hint = location_match.group(1)
                                    query = re.sub(r'\s+on\s+(?:my\s+)?\w+', '', query, flags=re.IGNORECASE)
                                else:
                                    location_hint = None
                                break
                
                if query:
                    # Remove "folder" from query if present
                    query = re.sub(r'\s+folder\s*$', '', query, flags=re.IGNORECASE).strip()
                    # Remove common words like "the", "my", "a", "an" from the start
                    query = re.sub(r'^(the|my|a|an)\s+', '', query, flags=re.IGNORECASE).strip()
                    if query:
                        return {
                            "mode": "tool",
                            "tool_name": "search_files",
                            "arguments": {
                                "query": query,
                                "location_hint": location_hint
                            }
                        }
            else:
                return {
                    "mode": "tool",
                    "tool_name": tool_name,
                    "arguments": {}
                }
    
    # LLM fallback for ambiguous cases (use better model for accuracy)
    prompt = f"""Route user message to tool or chat.

State: disc={packet["state"]["disc"]}, tasks={packet["state"]["tasks"]}
Tools: {tools_text}

Return JSON: {{"mode":"tool"|"chat","tool_name":"intent"|null,"arguments":{{}}|null}}

Examples:
"How are you?" → {{"mode":"chat","tool_name":null,"arguments":null}}
"rip the disc" → {{"mode":"tool","tool_name":"rip_disc","arguments":{{}}}}
"scan plex" → {{"mode":"tool","tool_name":"scan_plex","arguments":{{}}}}
"download https://youtube.com/xyz" → {{"mode":"tool","tool_name":"download","arguments":{{"url":"https://youtube.com/xyz"}}}}
"what is 2+2" → {{"mode":"tool","tool_name":"calculate","arguments":{{"query":"2+2"}}}}

Message: {packet["msg"]}"""

    try:
        try:
            # Use mistral-small for better accuracy while keeping speed
            response = groq_client.chat.completions.create(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0,
                response_format={"type": "json_object"}
            )
        except (TypeError, Exception):
            response = groq_client.chat.completions.create(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt + "\n\nReturn ONLY valid JSON, no other text."}],
                max_tokens=100,
                temperature=0
            )
        
        model_time = (time.time() - model_start) * 1000
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        json_match = re.search(r'\{[^{}]*"mode"[^{}]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        result = json.loads(content)
        mode = result.get("mode", "chat")
        tool_name = result.get("tool_name")
        
        if mode == "tool" and tool_name == "download" and not result.get("arguments", {}).get("url"):
            url_match = re.search(r'https?://[^\s]+', packet["msg"])
            if url_match:
                result["arguments"] = {"url": url_match.group(0)}
        
        return {
            "mode": mode,
            "tool_name": tool_name,
            "arguments": result.get("arguments") or {}
        }
    except Exception as e:
        return {"mode": "chat", "tool_name": None, "arguments": {}}


def _validate_tool(tool_name: str, glow_state: Any) -> tuple:
    """Validate tool can run given current GlowState"""
    if not tool_name or not SUPERPOWERS:
        return False, None
    
    # Fast cache lookup
    superpower_name = _TOOL_CACHE.get(tool_name)
    if not superpower_name:
        return False, None
    
    superpower = SUPERPOWERS.get(superpower_name)
    if not superpower or not hasattr(superpower, 'intent_map') or tool_name not in superpower.intent_map:
        return False, None
    
    # State-based validation
    if tool_name == "rip_disc" and not glow_state.device.disc_mounted:
        return False, "I don't see a disc inserted. Pop one in and I'll rip it."
    
    return True, None


async def route_message(user_message: str, glow_state: Any = None) -> Dict:
    """
    Main router entry point. Always runs first.
    Optimized for <100ms routing speed.
    """
    router_start = time.time()
    
    # Check warmup status
    if not _ROUTER_WARMED:
        await _warm_router()
    
    if not glow_state:
        from glowos.glow_state import glow_state_store
        glow_state = glow_state_store.get_state()
    
    packet = _build_router_packet(user_message, glow_state)
    router_output = await _call_router_model(packet)
    mode = router_output.get("mode", "chat")
    tool_name = router_output.get("tool_name")
    arguments = router_output.get("arguments", {})
    
    if mode == "tool" and tool_name:
        can_run, error_msg = _validate_tool(tool_name, glow_state)
        
        if not can_run:
            return {
                "mode": "chat",
                "tool_name": None,
                "arguments": {},
                "superpower_name": None,
                "fallback_reason": error_msg or "Tool not available"
            }
        
        # Use cache for fast lookup
        superpower_name = _TOOL_CACHE.get(tool_name)
        
        return {
            "mode": "tool",
            "tool_name": tool_name,
            "arguments": arguments,
            "superpower_name": superpower_name
        }
    
    return {
        "mode": "chat",
        "tool_name": None,
        "arguments": {},
        "superpower_name": None
    }


async def execute_tool(
    tool_name: str,
    arguments: Dict,
    superpower_name: str,
    glow_state: Any = None
) -> Dict:
    """Execute a tool and update GlowState. Returns tool result."""
    tool_start = time.time()
    print(f"🔧 Executing tool: {tool_name} ({superpower_name})")
    
    if not glow_state:
        from glowos.glow_state import glow_state_store
        glow_state = glow_state_store.get_state()
    
    # Fast lookup using cache
    superpower = SUPERPOWERS.get(superpower_name) if superpower_name else None
    
    if not superpower or not hasattr(superpower, 'intent_map') or tool_name not in superpower.intent_map:
        tool_time = (time.time() - tool_start) * 1000
        print(f"❌ Tool execution failed ({tool_time:.1f}ms): Superpower {superpower_name} not found")
        return {"error": f"Superpower {superpower_name} not found or doesn't handle {tool_name}"}
    
    task_id = str(uuid.uuid4())
    from glowos.glow_state import glow_state_store, TaskInfo
    
    task = TaskInfo(
        id=task_id,
        type=tool_name,
        status="running",
        progress=0.0,
        started_at=datetime.utcnow()
    )
    
    current_state = glow_state_store.get_state()
    current_state.tasks.active.append(task)
    glow_state_store.replace(current_state)
    
    # Pass task_id to tools that support progress updates (like rip_disc)
    if tool_name == "rip_disc" and "session_id" not in arguments:
        arguments["session_id"] = task_id
    
    try:
        result = await superpower.run(tool_name, **arguments)
        
        current_state = glow_state_store.get_state()
        for t in current_state.tasks.active:
            if t.id == task_id:
                t.status = "done"
                t.progress = 1.0
                t.finished_at = datetime.utcnow()
                break
        glow_state_store.replace(current_state)
        
        tool_time = (time.time() - tool_start) * 1000
        print(f"✅ Tool execution complete: {tool_time:.1f}ms")
        
        return result
        
    except Exception as e:
        current_state = glow_state_store.get_state()
        for t in current_state.tasks.active:
            if t.id == task_id:
                t.status = "error"
                t.message = str(e)
                t.finished_at = datetime.utcnow()
                break
        glow_state_store.replace(current_state)
        
        tool_time = (time.time() - tool_start) * 1000
        print(f"❌ Tool execution error ({tool_time:.1f}ms): {e}")
        
        return {"error": str(e)}
