"""
💬 Chat Routes - Conversation endpoints
Handles chat interactions, history, and transcription
"""
import json
import os
import asyncio
from fastapi import APIRouter, Request, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse
from datetime import datetime

from config import supabase, whisper_model, client, claude, openai_client
from services.memory import (
    get_or_create_thread,
    log_message_to_db,
    get_thread_messages_for_context,
    embed_text_ollama,
    select_memories_for_context
)
from services.intent_detection import detect_user_intent
from services.persona import build_persona_prompt, log_to_memory
from services.consciousness_tracker import analyze_and_save_state
from services.glow_router import route_message, execute_tool, set_superpowers as set_router_superpowers

router = APIRouter()

# Import SUPERPOWERS from main (we'll pass it as a dependency)
SUPERPOWERS = None
websocket_manager = None

def set_superpowers(superpowers):
    """Called from main.py to inject SUPERPOWERS dependency"""
    global SUPERPOWERS
    SUPERPOWERS = superpowers
    set_router_superpowers(superpowers)

def set_websocket_manager(ws_manager):
    """Called from main.py to inject WebSocket manager"""
    global websocket_manager
    websocket_manager = ws_manager


@router.get("/chat-history/{thread_id}", response_class=JSONResponse)
async def get_chat_history(thread_id: str):
    """Get chat history WITHOUT embeddings to reduce token usage"""
    try:
        messages = supabase.table("chat_messages")\
            .select("id, thread_id, role, content, metadata, created_at")\
            .eq("thread_id", thread_id)\
            .order("created_at", ascending=True)\
            .execute()
        data = getattr(messages, "data", [])
        return data
    except Exception as e:
        print("❌ Failed to fetch chat history:", e)
        return []


@router.get("/token-usage/{user_id}", response_class=JSONResponse)
async def get_token_usage(user_id: str):
    """Returns total token usage per model for a given user"""
    try:
        resp = supabase.table("token_usage")\
            .select("model_name, tokens_used")\
            .eq("user_id", user_id)\
            .execute()
        return getattr(resp, "data", [])
    except Exception as e:
        return {"error": str(e)}


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file using Whisper"""
    try:
        # Save the uploaded file
        contents = await file.read()
        with open("temp_audio.wav", "wb") as f:
            f.write(contents)

        # Run Whisper
        result = whisper_model.transcribe("temp_audio.wav")

        return {"text": result["text"]}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# /chat Endpoint - Cleaned, Modular, and Robust
# ============================================================

@router.post("/chat", response_class=JSONResponse)
async def chat_with_assistant(request: Request, background_tasks: BackgroundTasks):
    """
    Handles user chat input, persona context, memory retrieval (RAG),
    intent detection (Mistral), and response generation using multiple models.
    """

    # ============================================================
    # 1. Parse & Validate Incoming Request
    # ============================================================
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or empty JSON."})

    # ---- Persona & Session ----
    persona_id = data.get("id")
    system_prompt = data.get("system_prompt", "You are a helpful assistant.")
    session_priming = data.get("session_priming", "")
    tone_rules = data.get("tone_rules", "")
    chat_style = data.get("chat_style", {}) or {}
    mirroring_method = data.get("mirroring_method", "")
    style_guide = data.get("style_guide", "")
    values_and_philosophy = data.get("guiding_principles", "")
 
    # ---- Memory Retrieval ----
    memory_ids = data.get("memory_ids", [])
    use_memory_rag = data.get("use_memory_rag", True)

    # ---- User Input & Model Selection ----
    user_input = (data.get("message") or "").strip()
    thread_id = data.get("thread_id")
    user_id = data.get("user_id")  # optional if creating new thread
    selected_model = data.get("model", "Groq")
    use_mistral = data.get("useMistral", True)
    deep_memory = data.get("deepMemory", False)

    # ---- Health Data ----
    health_data = data.get("health_data", [])

    # ---- Validate Mandatory Fields ----
    if not thread_id and not user_id:
        return JSONResponse(status_code=400, content={"error": "Missing thread_id and user_id."})
    if not user_input:
        return JSONResponse(status_code=400, content={"error": "Message is required."})

    if not thread_id:
        thread_id = await get_or_create_thread(user_id)

    # Update GlowState with current model immediately
    from glowos.glow_state import glow_state_store
    model_map = {
        "Groq": "llama-3.1-8b-instant",
        "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
        "Claude": "claude-3.5-sonnet-20240620",
        "GPT-4o": "gpt-4o-2024-11-20",
    }
    active_model = model_map.get(selected_model, selected_model)
    glow_state_store.update(runtime={"active_model": active_model})

    # Log user message with model in metadata
    user_message_result = await log_message_to_db(
        thread_id, 
        "user", 
        user_input,
        metadata={"model": selected_model, "persona_name": data.get("name")}
    )
    user_message_id = None
    if user_message_result and isinstance(user_message_result, dict):
        user_message_id = user_message_result.get("id")
    elif isinstance(user_message_result, list) and len(user_message_result) > 0:
        user_message_id = user_message_result[0].get("id")
    
    # ============================================================
    # 🚀 ROUTER FIRST - Always-on intent detection
    # ============================================================
    import time
    request_start = time.time()
    
    current_state = glow_state_store.get_state()
    
    route_result = await route_message(user_input, current_state)
    mode = route_result.get("mode", "chat")
    tool_name = route_result.get("tool_name")
    arguments = route_result.get("arguments", {})
    superpower_name = route_result.get("superpower_name")
    
    # Handle tool execution
    if mode == "tool" and tool_name and superpower_name:
        tool_exec_start = time.time()
        
        # Check for fallback reason (tool not available)
        if route_result.get("fallback_reason"):
            response_text = route_result["fallback_reason"]
            await log_message_to_db(thread_id, "assistant", response_text)
            total_time = (time.time() - request_start) * 1000
            print(f"⏱️  Total request time: {total_time:.1f}ms (tool fallback)")
            print(f"{'='*60}\n")
            return {"response": response_text}
        
        # Special handling for Notion
        notion_connected = data.get("notionConnected", False)
        if superpower_name == "Notion Deep Memory" and not notion_connected:
            response_text = "🔒 Notion is DISCONNECTED. Enable the database button in the toolbar to use Notion features."
            await log_message_to_db(thread_id, "assistant", response_text)
            return {"response": response_text}
        
        # Add disc_path for rip_disc if available
        if tool_name == "rip_disc" and current_state.device.disc_path:
            arguments["disc_path"] = current_state.device.disc_path
        
        # Extract file paths for bulk_rename
        if tool_name == "bulk_rename":
            import re
            file_paths = []
            file_paths_match = re.search(r'File paths:\s*\n((?:.+\n?)+)', user_input)
            if file_paths_match:
                file_paths = [p.strip() for p in file_paths_match.group(1).strip().split('\n') if p.strip()]
            else:
                file_matches = re.findall(r'- (.+?) \((\w+)\)', user_input)
                dir_match = re.search(r'directory "(.+?)"', user_input)
                base_dir = dir_match.group(1) if dir_match else ""
                for filename, file_type in file_matches:
                    if file_type == "file":
                        if base_dir:
                            file_paths.append(os.path.join(base_dir, filename))
                        else:
                            file_paths.append(filename)
            if file_paths:
                arguments["file_paths"] = file_paths
                            
            pattern_match = re.search(r'([A-Za-z0-9\s\(\)]+?)\s*-\s*([Ss]\d+[Ee]\d+)', user_input)
            if pattern_match:
                arguments["details"] = f"{pattern_match.group(1)} - {pattern_match.group(2)}"
        
        # Execute tool
        try:
            result = await execute_tool(tool_name, arguments, superpower_name, current_state)
            tool_exec_time = (time.time() - tool_exec_start) * 1000
            
            # Format tool result
            if isinstance(result, dict) and result.get("type") == "plex_video":
                response_text = result.get("message", "Video ready to play")
                await log_message_to_db(thread_id, "assistant", response_text)
                return {
                    "response": response_text,
                    "plex_video": result,
                    "memories": [],
                    "memory_count": 0,
                    "superpower_name": superpower_name,
                    "tool_result": {
                        "status": "success",
                        "message": response_text,
                        "superpower": superpower_name,
                        "tool": tool_name
                    }
                }
            elif isinstance(result, dict) and result.get("type") == "file_search":
                # File search results - return in format that triggers FileModal
                response_text = result.get("message", f"Found {result.get('count', 0)} matches")
                await log_message_to_db(thread_id, "assistant", response_text)
                return {
                    "response": response_text,
                    "file_search": {
                        "matches": result.get("matches", []),
                        "query": result.get("query", ""),
                        "location_hint": result.get("location_hint"),
                        "count": result.get("count", 0)
                    },
                    "memories": [],
                    "memory_count": 0,
                    "superpower_name": superpower_name,
                    "tool_result": {
                        "status": "success",
                        "message": response_text,
                        "superpower": superpower_name,
                        "tool": tool_name,
                        "data": {
                            "input": arguments,
                            "output": result
                        }
                    }
                }
            else:
                # Format result message
                if isinstance(result, dict):
                    if result.get("error"):
                        status = "error"
                        message = result.get("error", "Tool execution failed")
                    elif result.get("success") is False:
                        status = "error"
                        message = result.get("message", "Tool execution failed")
                    elif result.get("message"):
                        status = "success"
                        message = result.get("message")
                    elif result.get("status"):
                        status = "success"
                        message = result.get("status")
                    elif tool_name in ("download", "download_video"):
                        status = "success"
                        message = "Download started successfully"
                    elif tool_name == "scan_plex":
                        status = "success"
                        message = "Plex library scan initiated"
                    elif tool_name == "rip_disc":
                        status = "success"
                        message = "Disc ripping started"
                    elif tool_name == "bulk_rename":
                        status = "success"
                        message = "Files renamed successfully"
                    else:
                        status = "success"
                        message = f"{tool_name.replace('_', ' ').title()} completed"
                else:
                    result_str = str(result)
                    if result_str.startswith("❌") or "error" in result_str.lower():
                        status = "error"
                        message = result_str.replace("❌", "").strip()
                    else:
                        status = "success"
                        message = result_str if result_str else "Task completed"
                
                await log_message_to_db(thread_id, "assistant", f"Executed {tool_name}")
                return {
                    "response": "",
                    "superpower_name": superpower_name,
                    "tool_result": {
                        "status": status,
                        "message": message,
                        "superpower": superpower_name,
                        "tool": tool_name,
                        "data": {
                            "input": arguments,
                            "output": result if isinstance(result, dict) else {"result": str(result)} if result else None
                        } if isinstance(result, dict) or result else {"input": arguments}
                    }
                }
        except Exception as e:
            tool_exec_time = (time.time() - tool_exec_start) * 1000
            await log_message_to_db(thread_id, "assistant", f"Error executing {tool_name}")
            return {
                "response": "",
                "superpower_name": superpower_name,
                "tool_result": {
                    "status": "error",
                    "message": str(e),
                    "superpower": superpower_name,
                    "tool": tool_name
                }
            }
    
    # ============================================================
    # CHAT PATH - Only runs if not tool/status
    # ============================================================
    chat_path_start = time.time()
    
    # Token limits per model (Groq limits)
    GROQ_TOKEN_LIMITS = {
        "llama-3.1-8b-instant": 8192,
        "llama-3.3-70b-versatile": 12000,
    }
    
    def estimate_tokens(text: str) -> int:
        """Rough token estimation: ~4 chars per token"""
        return len(text) // 4
    
    def truncate_memories(memories: list, max_tokens: int) -> tuple:
        """Truncate memories to fit token budget"""
        if not memories:
            return [], ""
        
        memory_strings = []
        total_tokens = 0
        
        for m in memories:
            memory_text = f"• ({round(m.get('similarity', 0.0) or 0.0, 3)}) {m.get('name', 'Memory')}: {m.get('content', '')}"
            mem_tokens = estimate_tokens(memory_text)
            
            if total_tokens + mem_tokens > max_tokens:
                # Truncate this memory to fit
                remaining = max_tokens - total_tokens - 50  # Reserve for header
                if remaining > 100:
                    content = m.get('content', '')
                    truncated_content = content[:remaining * 4] + "..."
                    memory_text = f"• ({round(m.get('similarity', 0.0) or 0.0, 3)}) {m.get('name', 'Memory')}: {truncated_content}"
                    memory_strings.append(memory_text)
                break
            
            memory_strings.append(memory_text)
            total_tokens += mem_tokens
        
        memory_block = f"## 🧠 Relevant Memories\n" + "\n".join(memory_strings) if memory_strings else ""
        return memories[:len(memory_strings)], memory_block
    
    def truncate_history(history: list, max_tokens: int) -> list:
        """Truncate conversation history to fit token budget"""
        if not history:
            return []
        
        total_tokens = 0
        truncated_history = []
        
        # Process in reverse (most recent first)
        for msg in reversed(history):
            content = msg.get('content', '')
            msg_tokens = estimate_tokens(content) + 10  # +10 for role/metadata overhead
            
            if total_tokens + msg_tokens > max_tokens:
                # Truncate this message
                remaining = max_tokens - total_tokens - 20
                if remaining > 50:
                    truncated_content = content[:remaining * 4] + "..."
                    truncated_msg = {**msg, 'content': truncated_content}
                    truncated_history.insert(0, truncated_msg)
                break
            
            truncated_history.insert(0, msg)
            total_tokens += msg_tokens
        
        return truncated_history
    
    # Analyze consciousness state (background)
    try:
        consciousness_state = await analyze_and_save_state(
            message_text=user_input,
            user_id=user_id,
            thread_id=thread_id,
            message_id=user_message_id,
            context="user_message"
        )
    except Exception as e:
        consciousness_state = None
    
    # Fetch chat history (will be truncated later if needed)
    history_messages = await get_thread_messages_for_context(thread_id, limit=20)
    
    # Memory Retrieval (RAG) - only for chat
    memory_block = ""
    selected_memories = []
    
    if use_memory_rag:
        query_embedding = await embed_text_ollama(user_input)
        match_count = 200 if not deep_memory else 60
        
        memory_resp = supabase.rpc(
            "match_memories",
            {"query_embedding": query_embedding, "match_count": match_count}
        ).execute()

        all_memories = getattr(memory_resp, "data", []) or []
        selected_memories, total_candidates, usable_candidates = select_memories_for_context(
            all_memories,
            deep_memory=deep_memory,
            limit=15
        )
    
    # Determine token budget based on model
    GROQ_MODEL_MAP = {
        "Groq": "llama-3.1-8b-instant",
        "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
    }
    model_name = GROQ_MODEL_MAP.get(selected_model, "llama-3.1-8b-instant")
    token_limit = GROQ_TOKEN_LIMITS.get(model_name, 8000)
    reserved_tokens = 2000
    available_tokens = token_limit - reserved_tokens
    
    memory_data = []
    if selected_memories:
        # Allocate tokens: 40% memories, 30% KB, 30% history
        memory_budget = int(available_tokens * 0.4)
        selected_memories, memory_block = truncate_memories(selected_memories, memory_budget)
        
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

    # Deep Memory - Notion Search (if enabled)
    notion_connected = data.get("notionConnected", False)
    if deep_memory and notion_connected:
        from services.superpower_loader import SUPERPOWERS
        if SUPERPOWERS and "Notion Deep Memory" in SUPERPOWERS:
            try:
                notion_power = SUPERPOWERS["Notion Deep Memory"]
                notion_results = await notion_power.run("search_notion", query=user_input)
                if notion_results and "No matching" not in str(notion_results):
                    memory_block += f"\n\n## 📚 Notion Deep Memory\n{notion_results}"
            except Exception:
                pass
    # ============================================================
    # KNOWLEDGE BASE INTEGRATION - Runs alongside memory
    # ============================================================
    knowledge_context = ""
    kb_sources = []
    use_kb = data.get("useKnowledgeBase", True)
    
    # Check for crisis keywords
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'self-harm', 'want to die',
        'hurt myself', 'end my life', 'no reason to live', 'better off dead'
    ]
    is_crisis = any(keyword in user_input.lower() for keyword in crisis_keywords)
    
    if is_crisis:
        print("🚨 CRISIS DETECTED - Fetching crisis resources")
        from services.knowledge_base import get_crisis_resources, format_knowledge_for_context
        crisis_resources = await get_crisis_resources()
        # Crisis resources are critical - use more tokens but still summarize intelligently
        knowledge_context = await format_knowledge_for_context(
            crisis_resources, 
            max_tokens=2000,
            use_summarization=True
        )
        kb_sources = [
            {
                "title": resource.get("title"),
                "category": resource.get("category"),
                "type": "crisis_resource"
            }
            for resource in crisis_resources
        ]
    elif use_kb:
        from services.knowledge_base import search_knowledge_base, format_knowledge_for_context
        knowledge_entries = await search_knowledge_base(query=user_input, limit=3)
        
        if knowledge_entries:
            knowledge_context = await format_knowledge_for_context(
                knowledge_entries, 
                max_tokens=1500,
                use_summarization=True
            )
            kb_sources = [
                {
                    "title": entry.get("title"),
                    "category": entry.get("category"),
                    "similarity": entry.get("similarity", 0),
                    "type": entry.get("content_type")
                }
                for entry in knowledge_entries
            ]
    # ============================================================
    # 5. Default LLM Response
    # ============================================================
    try:
        # Combine memory + knowledge base into one block
        combined_block = memory_block
        kb_budget = int(available_tokens * 0.3)
        
        if knowledge_context:
            kb_tokens = estimate_tokens(knowledge_context)
            if kb_tokens > kb_budget:
                kb_chars = kb_budget * 4
                knowledge_context = knowledge_context[:kb_chars] + "\n[... knowledge base truncated ...]"
            combined_block += f"\n\n{knowledge_context}"
        
        # Truncate history if needed
        history_budget = int(available_tokens * 0.3)
        history_tokens = sum(estimate_tokens(msg.get('content', '')) for msg in history_messages)
        if history_tokens > history_budget:
            history_messages = truncate_history(history_messages, history_budget)
        
        # Estimate total tokens and truncate if needed
        system_est = estimate_tokens(system_prompt)
        combined_est = estimate_tokens(combined_block)
        history_est = sum(estimate_tokens(msg.get('content', '')) for msg in history_messages)
        user_est = estimate_tokens(user_input)
        total_est = system_est + combined_est + history_est + user_est + 500
        
        if total_est > token_limit:
            remaining = token_limit - system_est - combined_est - user_est - 1000
            if remaining > 500:
                history_messages = truncate_history(history_messages, remaining)
        
        # Add crisis handling to system prompt if needed
        crisis_instructions = ""
        if is_crisis:
            crisis_instructions = """
    🚨 CRITICAL - CRISIS RESPONSE PROTOCOL:
    The user may be in crisis. You MUST:
    1. Immediately acknowledge their pain with compassion
    2. Provide crisis resources PROMINENTLY (988, Crisis Text Line, 911)
    3. Encourage professional help NOW
    4. Stay supportive and validating
    5. Do NOT attempt therapy - connect them to professionals
    """

        # Get current GlowState
        from glowos.glow_state import glow_state_store
        current_state = glow_state_store.get_state()
        glow_state_dict = current_state.dict()  # Convert Pydantic model to dict

        # Build messages using persona fields + knowledge base
        messages = build_persona_prompt(
            system_prompt + crisis_instructions if is_crisis else system_prompt,
            session_priming,
            tone_rules,
            chat_style,
            mirroring_method,
            style_guide,
            values_and_philosophy,
            combined_block,
            history_messages,
            user_input,
            glow_state=glow_state_dict
        )

        # Claude
        if selected_model == "Claude":
            response = claude.messages.create(
                model="claude-3.5-sonnet-20240620",
                max_tokens=1024,
                temperature=0.7,
                messages=messages
            )
            reply = response.content[0].text.strip()

        # OpenAI GPT-4o
        elif selected_model == "GPT-4o":
            response = openai_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=messages,
                temperature=chat_style.get("temperature", 0.7),
                top_p=chat_style.get("top_p", 1.0),
                presence_penalty=chat_style.get("presence_penalty", 0.0),
                frequency_penalty=chat_style.get("frequency_penalty", 0.0)
            )
            reply = response.choices[0].message.content.strip()

        # Groq models (fallback)
        else:
            model_name = GROQ_MODEL_MAP.get(selected_model, "llama-3.1-8b-instant")

            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=chat_style.get("temperature", 0.7),
                    top_p=chat_style.get("top_p", 1.0),
                    presence_penalty=chat_style.get("presence_penalty", 0.0),
                    frequency_penalty=chat_style.get("frequency_penalty", 0.0)
                )
                reply = response.choices[0].message.content.strip()
            except Exception as groq_error:
                error_str = str(groq_error)
                if "413" in error_str or "token" in error_str.lower() or "TPM" in error_str:
                    print(f"⚠️  Token limit error, retrying with reduced context...")
                    # Aggressively reduce context and retry once
                    history_messages = truncate_history(history_messages, 1000)
                    combined_block = memory_block[:500] if memory_block else ""
                    
                    messages = build_persona_prompt(
                        system_prompt + crisis_instructions if is_crisis else system_prompt,
                        session_priming,
                        tone_rules,
                        chat_style,
                        mirroring_method,
                        style_guide,
                        values_and_philosophy,
                        combined_block,
                        history_messages,
                        user_input,
                        glow_state=glow_state_dict
                    )
                    
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            temperature=chat_style.get("temperature", 0.7),
                            top_p=chat_style.get("top_p", 1.0),
                            presence_penalty=chat_style.get("presence_penalty", 0.0),
                            frequency_penalty=chat_style.get("frequency_penalty", 0.0)
                        )
                        reply = response.choices[0].message.content.strip()
                        print(f"✅ Retry successful with reduced context")
                    except Exception as retry_error:
                        raise Exception(f"Token limit exceeded even after reduction. Please use a smaller model or reduce context. Original: {error_str}")
                else:
                    raise

        assistant_message_result = await log_message_to_db(
            thread_id, 
            "assistant", 
            reply,
            metadata={"model": selected_model}
        )
        assistant_message_id = None
        if assistant_message_result:
            try:
                if hasattr(assistant_message_result, 'data') and assistant_message_result.data:
                    assistant_message_id = assistant_message_result.data[0].get("id") if isinstance(assistant_message_result.data, list) else assistant_message_result.data.get("id")
            except:
                pass

        # Return response with memories AND knowledge base sources
        chat_path_time = (time.time() - chat_path_start) * 1000
        total_time = (time.time() - request_start) * 1000
        
        result = {
            "response": reply,
            "memories": memory_data,
            "memory_count": len(memory_data),
            "knowledge_base": kb_sources,
            "kb_count": len(kb_sources),
            "is_crisis": is_crisis,
            "consciousness_state": consciousness_state if 'consciousness_state' in locals() else None,
            "token_usage": {
                "prompt_tokens": prompt_tokens if 'prompt_tokens' in locals() else 0,
                "completion_tokens": completion_tokens if 'completion_tokens' in locals() else 0,
                "total_tokens": total_tokens if 'total_tokens' in locals() else 0
            }
        }
        
        return result

    except Exception as e:
        error_msg = f"❌ Chat handler error: {str(e)}"
        log_to_memory("glos", error_msg)
        print(error_msg)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/chat-title", response_class=JSONResponse)
async def generate_chat_title(request: Request):
    """Generate a short, friendly title for a chat thread."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or empty JSON."})

    user_text = (data.get("user") or "").strip()
    assistant_text = (data.get("assistant") or "").strip()

    if not user_text:
        return JSONResponse(status_code=400, content={"error": "User text is required."})

    system_prompt = (
        "You create concise, engaging chat titles (max 40 characters). "
        "Write Title Case text with no surrounding quotes or trailing punctuation."
    )
    conversation = f"User: {user_text}\nAssistant: {assistant_text or 'Pending'}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": conversation},
    ]

    try:
        if openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
                max_tokens=32,
            )
            title = response.choices[0].message.content.strip()
        else:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.2,
                max_tokens=32,
            )
            title = response.choices[0].message.content.strip()
    except Exception as error:
        print(f"❌ Failed to generate chat title: {error}")
        return JSONResponse(
            status_code=500, content={"error": "Unable to generate title."}
        )

    clean_title = title.replace("\n", " ").replace('"', "").strip()
    if len(clean_title) > 60:
        clean_title = clean_title[:57].rstrip() + "..."

    return {"title": clean_title}


async def chat_with_assistant_stream(data: dict, client_id: str):
    """Stream AI response via WebSocket - includes all routing, memory, KB logic"""
    if not websocket_manager:
        return
    
    # Check if cancelled
    def is_cancelled():
        return client_id in getattr(websocket_manager, 'cancelled_chats', set())
    
    try:
        # ============================================================
        # 1. Parse & Validate (same as regular chat)
        # ============================================================
        user_input = (data.get("message") or "").strip()
        thread_id = data.get("thread_id")
        user_id = data.get("user_id")
        selected_model = data.get("model", "Groq")
        use_memory_rag = data.get("use_memory_rag", True)
        deep_memory = data.get("deepMemory", False)
        use_mistral = data.get("useMistral", True)
        notion_connected = data.get("notionConnected", False)
        
        if not thread_id and not user_id:
            await websocket_manager.send_chat_chunk(client_id, "❌ Error: Missing thread_id and user_id.", True)
            return
        if not user_input:
            await websocket_manager.send_chat_chunk(client_id, "❌ Error: Message is required.", True)
            return
        
        if not thread_id:
            thread_id = await get_or_create_thread(user_id)
        
        # Update GlowState
        from glowos.glow_state import glow_state_store
        model_map = {
            "Groq": "llama-3.1-8b-instant",
            "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
            "Claude": "claude-3.5-sonnet-20240620",
            "GPT-4o": "gpt-4o-2024-11-20",
        }
        active_model = model_map.get(selected_model, selected_model)
        glow_state_store.update(runtime={"active_model": active_model})
        
        # Log user message
        user_message_result = await log_message_to_db(
            thread_id, "user", user_input,
            metadata={"model": selected_model, "persona_name": data.get("name")}
        )
        user_message_id = None
        if user_message_result and isinstance(user_message_result, dict):
            user_message_id = user_message_result.get("id")
        elif isinstance(user_message_result, list) and len(user_message_result) > 0:
            user_message_id = user_message_result[0].get("id")
        
        # ============================================================
        # 2. ROUTER - Intent detection & tool execution
        # ============================================================
        import time
        request_start = time.time()
        current_state = glow_state_store.get_state()
        route_result = await route_message(user_input, current_state)
        mode = route_result.get("mode", "chat")
        tool_name = route_result.get("tool_name")
        arguments = route_result.get("arguments", {})
        superpower_name = route_result.get("superpower_name")
        
        # Handle tool execution (send complete response, no streaming)
        if mode == "tool" and tool_name and superpower_name:
            if route_result.get("fallback_reason"):
                response_text = route_result["fallback_reason"]
                await log_message_to_db(thread_id, "assistant", response_text)
                await websocket_manager.send_chat_chunk(client_id, response_text, True)
                await websocket_manager.send_chat_metadata(client_id, {
                    "memories": [],
                    "memory_count": 0,
                    "knowledge_base": [],
                    "kb_count": 0,
                    "superpower_name": superpower_name,
                    "tool_result": {
                        "status": "error",
                        "message": response_text,
                        "superpower": superpower_name,
                        "tool": tool_name
                    }
                })
                return
            
            if superpower_name == "Notion Deep Memory" and not notion_connected:
                response_text = "🔒 Notion is DISCONNECTED. Enable the database button in the toolbar to use Notion features."
                await log_message_to_db(thread_id, "assistant", response_text)
                await websocket_manager.send_chat_chunk(client_id, response_text, True)
                await websocket_manager.send_chat_metadata(client_id, {
                    "memories": [],
                    "memory_count": 0,
                    "knowledge_base": [],
                    "kb_count": 0,
                    "superpower_name": superpower_name
                })
                return
            
            if tool_name == "rip_disc" and current_state.device.disc_path:
                arguments["disc_path"] = current_state.device.disc_path
            
            if tool_name == "bulk_rename":
                import re
                file_paths = []
                file_paths_match = re.search(r'File paths:\s*\n((?:.+\n?)+)', user_input)
                if file_paths_match:
                    file_paths = [p.strip() for p in file_paths_match.group(1).strip().split('\n') if p.strip()]
                else:
                    file_matches = re.findall(r'- (.+?) \((\w+)\)', user_input)
                    dir_match = re.search(r'directory "(.+?)"', user_input)
                    base_dir = dir_match.group(1) if dir_match else ""
                    for filename, file_type in file_matches:
                        if file_type == "file":
                            if base_dir:
                                file_paths.append(os.path.join(base_dir, filename))
                            else:
                                file_paths.append(filename)
                if file_paths:
                    arguments["file_paths"] = file_paths
                pattern_match = re.search(r'([A-Za-z0-9\s\(\)]+?)\s*-\s*([Ss]\d+[Ee]\d+)', user_input)
                if pattern_match:
                    arguments["details"] = f"{pattern_match.group(1)} - {pattern_match.group(2)}"
            
            try:
                result = await execute_tool(tool_name, arguments, superpower_name, current_state)
                if isinstance(result, dict) and result.get("type") == "plex_video":
                    response_text = result.get("message", "Video ready to play")
                    await log_message_to_db(thread_id, "assistant", response_text)
                    await websocket_manager.send_chat_chunk(client_id, response_text, True)
                    await websocket_manager.send_chat_metadata(client_id, {
                        "memories": [],
                        "memory_count": 0,
                        "knowledge_base": [],
                        "kb_count": 0,
                        "superpower_name": superpower_name,
                        "tool_result": {
                            "status": "success",
                            "message": response_text,
                            "superpower": superpower_name,
                            "tool": tool_name
                        },
                        "plex_video": result
                    })
                    return
                elif isinstance(result, dict) and result.get("type") == "file_search":
                    # File search results - return in format that triggers FileModal
                    count = result.get("count", 0)
                    query = result.get("query", "")
                    response_text = result.get("message", f"🔍 Found {count} match{'es' if count != 1 else ''} for '{query}'")
                    await log_message_to_db(thread_id, "assistant", response_text)
                    # Send the response text first
                    await websocket_manager.send_chat_chunk(client_id, response_text, False)
                    # Then send metadata with file_search data
                    await websocket_manager.send_chat_metadata(client_id, {
                        "memories": [],
                        "memory_count": 0,
                        "knowledge_base": [],
                        "kb_count": 0,
                        "superpower_name": superpower_name,
                        "tool_result": {
                            "status": "success",
                            "message": response_text,
                            "superpower": superpower_name,
                            "tool": tool_name,
                            "data": {
                                "input": arguments,
                                "output": result
                            }
                        },
                        "file_search": {
                            "matches": result.get("matches", []),
                            "query": result.get("query", ""),
                            "location_hint": result.get("location_hint"),
                            "count": result.get("count", 0)
                        }
                    })
                    # Send final chunk to mark as done
                    await websocket_manager.send_chat_chunk(client_id, "", True)
                    return
                else:
                    if isinstance(result, dict):
                        if result.get("error"):
                            status = "error"
                            message = result.get("error", "Tool execution failed")
                        elif result.get("success") is False:
                            status = "error"
                            message = result.get("message", "Tool execution failed")
                        elif result.get("message"):
                            status = "success"
                            message = result.get("message")
                        elif result.get("status"):
                            status = "success"
                            message = result.get("status")
                        else:
                            status = "success"
                            message = f"{tool_name.replace('_', ' ').title()} completed"
                    else:
                        result_str = str(result)
                        if result_str.startswith("❌"):
                            status = "error"
                            message = result_str.replace("❌", "").strip()
                        else:
                            status = "success"
                            message = result_str if result_str else "Task completed"
                    await log_message_to_db(thread_id, "assistant", f"Executed {tool_name}")
                    await websocket_manager.send_chat_chunk(client_id, message, True)
                    await websocket_manager.send_chat_metadata(client_id, {
                        "memories": [],
                        "memory_count": 0,
                        "knowledge_base": [],
                        "kb_count": 0,
                        "superpower_name": superpower_name,
                        "tool_result": {
                            "status": status,
                            "message": message,
                            "superpower": superpower_name,
                            "tool": tool_name,
                            "data": {
                                "input": arguments,
                                "output": result if isinstance(result, dict) else {"result": str(result)} if result else None
                            } if isinstance(result, dict) or result else {"input": arguments}
                        }
                    })
                    return
            except Exception as e:
                await log_message_to_db(thread_id, "assistant", f"Error executing {tool_name}")
                await websocket_manager.send_chat_chunk(client_id, f"❌ Error: {str(e)}", True)
                await websocket_manager.send_chat_metadata(client_id, {
                    "memories": [],
                    "memory_count": 0,
                    "knowledge_base": [],
                    "kb_count": 0,
                    "superpower_name": superpower_name,
                    "tool_result": {
                        "status": "error",
                        "message": str(e),
                        "superpower": superpower_name,
                        "tool": tool_name
                    }
                })
                return
        
        # ============================================================
        # 3. CHAT PATH - Full logic with memory, KB, etc.
        # ============================================================
        GROQ_TOKEN_LIMITS = {
            "llama-3.1-8b-instant": 8192,
            "llama-3.3-70b-versatile": 12000,
        }
        
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        def truncate_memories(memories: list, max_tokens: int) -> tuple:
            if not memories:
                return [], ""
            memory_strings = []
            total_tokens = 0
            for m in memories:
                memory_text = f"• ({round(m.get('similarity', 0.0) or 0.0, 3)}) {m.get('name', 'Memory')}: {m.get('content', '')}"
                mem_tokens = estimate_tokens(memory_text)
                if total_tokens + mem_tokens > max_tokens:
                    remaining = max_tokens - total_tokens - 50
                    if remaining > 100:
                        content = m.get('content', '')
                        truncated_content = content[:remaining * 4] + "..."
                        memory_text = f"• ({round(m.get('similarity', 0.0) or 0.0, 3)}) {m.get('name', 'Memory')}: {truncated_content}"
                        memory_strings.append(memory_text)
                    break
                memory_strings.append(memory_text)
                total_tokens += mem_tokens
            memory_block = f"## 🧠 Relevant Memories\n" + "\n".join(memory_strings) if memory_strings else ""
            return memories[:len(memory_strings)], memory_block
        
        def truncate_history(history: list, max_tokens: int) -> list:
            if not history:
                return []
            total_tokens = 0
            truncated_history = []
            for msg in reversed(history):
                content = msg.get('content', '')
                msg_tokens = estimate_tokens(content) + 10
                if total_tokens + msg_tokens > max_tokens:
                    remaining = max_tokens - total_tokens - 20
                    if remaining > 50:
                        truncated_content = content[:remaining * 4] + "..."
                        truncated_msg = {**msg, 'content': truncated_content}
                        truncated_history.insert(0, truncated_msg)
                    break
                truncated_history.insert(0, msg)
                total_tokens += msg_tokens
            return truncated_history
        
        # Analyze consciousness state
        try:
            consciousness_state = await analyze_and_save_state(
                message_text=user_input,
                user_id=user_id,
                thread_id=thread_id,
                message_id=user_message_id,
                context="user_message"
            )
        except Exception:
            consciousness_state = None
        
        # Fetch chat history
        history_messages = await get_thread_messages_for_context(thread_id, limit=20)
        
        # Memory Retrieval (RAG)
        memory_block = ""
        selected_memories = []
        if use_memory_rag:
            query_embedding = await embed_text_ollama(user_input)
            match_count = 200 if not deep_memory else 60
            memory_resp = supabase.rpc(
                "match_memories",
                {"query_embedding": query_embedding, "match_count": match_count}
            ).execute()
            all_memories = getattr(memory_resp, "data", []) or []
            selected_memories, total_candidates, usable_candidates = select_memories_for_context(
                all_memories, deep_memory=deep_memory, limit=15
            )
        
        GROQ_MODEL_MAP = {
            "Groq": "llama-3.1-8b-instant",
            "Groq-LLaMA3-70B": "llama-3.3-70b-versatile",
        }
        model_name = GROQ_MODEL_MAP.get(selected_model, "llama-3.1-8b-instant")
        token_limit = GROQ_TOKEN_LIMITS.get(model_name, 8000)
        reserved_tokens = 2000
        available_tokens = token_limit - reserved_tokens
        
        memory_data = []
        if selected_memories:
            memory_budget = int(available_tokens * 0.4)
            selected_memories, memory_block = truncate_memories(selected_memories, memory_budget)
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
        
        # Deep Memory - Notion Search
        if deep_memory and notion_connected:
            if SUPERPOWERS and "Notion Deep Memory" in SUPERPOWERS:
                try:
                    notion_power = SUPERPOWERS["Notion Deep Memory"]
                    notion_results = await notion_power.run("search_notion", query=user_input)
                    if notion_results and "No matching" not in str(notion_results):
                        memory_block += f"\n\n## 📚 Notion Deep Memory\n{notion_results}"
                except Exception:
                    pass
        
        # Knowledge Base Integration
        knowledge_context = ""
        kb_sources = []
        use_kb = data.get("useKnowledgeBase", True)
        crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'self-harm', 'want to die',
            'hurt myself', 'end my life', 'no reason to live', 'better off dead'
        ]
        is_crisis = any(keyword in user_input.lower() for keyword in crisis_keywords)
        
        if is_crisis:
            from services.knowledge_base import get_crisis_resources, format_knowledge_for_context
            crisis_resources = await get_crisis_resources()
            knowledge_context = await format_knowledge_for_context(
                crisis_resources, max_tokens=2000, use_summarization=True
            )
            kb_sources = [
                {"title": resource.get("title"), "category": resource.get("category"), "type": "crisis_resource"}
                for resource in crisis_resources
            ]
        elif use_kb:
            from services.knowledge_base import search_knowledge_base, format_knowledge_for_context
            knowledge_entries = await search_knowledge_base(query=user_input, limit=3)
            if knowledge_entries:
                knowledge_context = await format_knowledge_for_context(
                    knowledge_entries, max_tokens=1500, use_summarization=True
                )
                kb_sources = [
                    {
                        "title": entry.get("title"),
                        "category": entry.get("category"),
                        "similarity": entry.get("similarity", 0),
                        "type": entry.get("content_type")
                    }
                    for entry in knowledge_entries
                ]
        
        # Combine memory + knowledge base
        combined_block = memory_block
        kb_budget = int(available_tokens * 0.3)
        if knowledge_context:
            kb_tokens = estimate_tokens(knowledge_context)
            if kb_tokens > kb_budget:
                kb_chars = kb_budget * 4
                knowledge_context = knowledge_context[:kb_chars] + "\n[... knowledge base truncated ...]"
            combined_block += f"\n\n{knowledge_context}"
        
        # Truncate history
        history_budget = int(available_tokens * 0.3)
        history_tokens = sum(estimate_tokens(msg.get('content', '')) for msg in history_messages)
        if history_tokens > history_budget:
            history_messages = truncate_history(history_messages, history_budget)
        
        # Crisis instructions
        crisis_instructions = ""
        if is_crisis:
            crisis_instructions = """
    🚨 CRITICAL - CRISIS RESPONSE PROTOCOL:
    The user may be in crisis. You MUST:
    1. Immediately acknowledge their pain with compassion
    2. Provide crisis resources PROMINENTLY (988, Crisis Text Line, 911)
    3. Encourage professional help NOW
    4. Stay supportive and validating
    5. Do NOT attempt therapy - connect them to professionals
    """
        
        # Build messages
        system_prompt = data.get("system_prompt", "You are a helpful assistant.")
        current_state = glow_state_store.get_state()
        glow_state_dict = current_state.dict()
        messages = build_persona_prompt(
            system_prompt + crisis_instructions if is_crisis else system_prompt,
            data.get("session_priming", ""),
            data.get("tone_rules", ""),
            data.get("chat_style", {}) or {},
            data.get("mirroring_method", ""),
            data.get("style_guide", ""),
            data.get("guiding_principles", ""),
            combined_block,
            history_messages,
            user_input,
            glow_state=glow_state_dict
        )
        
        # Stream response based on model
        full_reply = ""
        chat_style = data.get("chat_style", {}) or {}
        
        if selected_model == "Claude":
            with claude.messages.stream(
                model="claude-3.5-sonnet-20240620",
                max_tokens=1024,
                temperature=0.7,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    if is_cancelled():
                        return
                    full_reply += text
                    await websocket_manager.send_chat_chunk(client_id, text, False)
        elif selected_model == "GPT-4o":
            response = openai_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=messages,
                stream=True,
                temperature=chat_style.get("temperature", 0.7),
                top_p=chat_style.get("top_p", 1.0),
                presence_penalty=chat_style.get("presence_penalty", 0.0),
                frequency_penalty=chat_style.get("frequency_penalty", 0.0)
            )
            for chunk in response:
                if is_cancelled():
                    return
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    await websocket_manager.send_chat_chunk(client_id, content, False)
        else:
            model_name = GROQ_MODEL_MAP.get(selected_model, "llama-3.1-8b-instant")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True,
                    temperature=chat_style.get("temperature", 0.7),
                    top_p=chat_style.get("top_p", 1.0),
                    presence_penalty=chat_style.get("presence_penalty", 0.0),
                    frequency_penalty=chat_style.get("frequency_penalty", 0.0)
                )
                for chunk in response:
                    if is_cancelled():
                        return
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_reply += content
                        await websocket_manager.send_chat_chunk(client_id, content, False)
            except Exception as groq_error:
                error_str = str(groq_error)
                if "413" in error_str or "token" in error_str.lower() or "TPM" in error_str:
                    # Retry with reduced context
                    history_messages = truncate_history(history_messages, 1000)
                    combined_block = memory_block[:500] if memory_block else ""
                    messages = build_persona_prompt(
                        system_prompt + crisis_instructions if is_crisis else system_prompt,
                        data.get("session_priming", ""),
                        data.get("tone_rules", ""),
                        chat_style,
                        data.get("mirroring_method", ""),
                        data.get("style_guide", ""),
                        data.get("guiding_principles", ""),
                        combined_block,
                        history_messages,
                        user_input,
                        glow_state=glow_state_dict
                    )
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        stream=True,
                        temperature=chat_style.get("temperature", 0.7),
                        top_p=chat_style.get("top_p", 1.0),
                        presence_penalty=chat_style.get("presence_penalty", 0.0),
                        frequency_penalty=chat_style.get("frequency_penalty", 0.0)
                    )
                    for chunk in response:
                        if is_cancelled():
                            return
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_reply += content
                            await websocket_manager.send_chat_chunk(client_id, content, False)
        
        # Check if cancelled before finalizing
        if is_cancelled():
            return
        
        # Log and finalize
        await log_message_to_db(thread_id, "assistant", full_reply, metadata={"model": selected_model})
        
        # Send metadata (memories, KB sources, etc.)
        await websocket_manager.send_chat_metadata(client_id, {
            "memories": memory_data,
            "memory_count": len(memory_data),
            "knowledge_base": kb_sources,
            "kb_count": len(kb_sources),
            "is_crisis": is_crisis,
            "consciousness_state": consciousness_state if consciousness_state else None
        })
        
        # Send final chunk with done flag (if not cancelled)
        if not is_cancelled():
            await websocket_manager.send_chat_chunk(client_id, "", True)
        
        # Clean up cancelled flag
        if hasattr(websocket_manager, 'cancelled_chats'):
            websocket_manager.cancelled_chats.discard(client_id)
        
    except asyncio.CancelledError:
        # Chat was cancelled
        if hasattr(websocket_manager, 'cancelled_chats'):
            websocket_manager.cancelled_chats.discard(client_id)
        print(f"📛 Chat stream cancelled for {client_id}")
    except Exception as e:
        if not is_cancelled():
            await websocket_manager.send_chat_chunk(client_id, f"\n\n❌ Error: {str(e)}", True)
        print(f"❌ Chat stream error: {e}")
        if hasattr(websocket_manager, 'cancelled_chats'):
            websocket_manager.cancelled_chats.discard(client_id)

__all__ = ["router", "set_superpowers", "set_websocket_manager", "chat_with_assistant_stream"]
