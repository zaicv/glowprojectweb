from datetime import datetime
from typing import List, Dict, Optional
import json

def build_persona_prompt(
    system_prompt: str,
    session_priming: str,
    tone_rules: str,
    chat_style: dict,
    mirroring_method: str,
    style_guide: str,
    values_and_philosophy: str,
    memory_block: str,
    history_messages: List[Dict],
    user_input: str,
    glow_state: Optional[Dict] = None
) -> List[Dict[str, str]]:
    """
    Builds a comprehensive prompt combining persona settings, memory, 
    knowledge base, and chat history.
    
    Args:
        system_prompt: Core system instructions
        session_priming: Session-specific context
        tone_rules: Tone and voice guidelines
        chat_style: Style parameters (temperature, etc.)
        mirroring_method: Communication mirroring approach
        style_guide: Detailed style instructions
        values_and_philosophy: Guiding principles
        memory_block: Combined memory + knowledge base context
        history_messages: Previous conversation messages
        user_input: Current user message
    
    Returns:
        List of message dictionaries for LLM
    """
    messages = []
    
    # Build comprehensive system message
    system_content = system_prompt
    
    if session_priming:
        system_content += f"\n\n## Session Context\n{session_priming}"
    
    if tone_rules:
        system_content += f"\n\n## Tone Rules\n{tone_rules}"
    
    if mirroring_method:
        system_content += f"\n\n## Communication Style\n{mirroring_method}"
    
    if style_guide:
        system_content += f"\n\n## Style Guide\n{style_guide}"
    
    if values_and_philosophy:
        system_content += f"\n\n## Guiding Principles\n{values_and_philosophy}"
    
    # Memory block now includes both memories AND knowledge base
    if memory_block:
        system_content += f"\n\n{memory_block}"


        # Add GlowState context if provided
    if glow_state:
        # Format GlowState in a clear, readable way
        runtime = glow_state.get("runtime", {})
        device = glow_state.get("device", {})
        system = glow_state.get("system", {})
        
        glow_state_text = f"""
## 🌟 Current System State (GlowState) - YOU MUST USE THIS FOR ACCURATE ANSWERS

**Runtime:**
- Active Model: {runtime.get("active_model", "Not set")}
- Persona: {runtime.get("persona", "Not set")}
- Superpowers Loaded: {", ".join(runtime.get("superpowers_loaded", [])) or "None"}
- Ollama Running: {"Yes" if runtime.get("ollama_running") else "No"}
- Plex Running: {"Yes" if runtime.get("plex_running") else "No"}

**Device:**
- Disc Inserted: {"YES" if device.get("disc_mounted") else "NO"}
- Disc Path: {device.get("disc_path", "N/A") if device.get("disc_mounted") else "N/A"}
- Recent Downloads: {len(device.get("downloads_recent", []))} files
- Frontmost App: {device.get("frontmost_app", "Unknown")}

**System:**
- CPU Usage: {system.get("cpu_usage", 0) * 100:.1f}%
- RAM Usage: {system.get("ram_usage", 0) * 100:.1f}%
- Disk Free: {system.get("disk_free_gb", 0):.1f} GB

**CRITICAL INSTRUCTIONS:**
- When asked about your model, ALWAYS use the exact model name from "Active Model" above
- When asked about a disc, check "Disc Inserted" - if NO, say no disc is inserted
- When asked about superpowers, list ONLY the superpowers from "Superpowers Loaded" above
- When asked about system status, use the exact values from System section above
- DO NOT make up or guess information - ALWAYS use the values from GlowState
"""
        system_content += glow_state_text
    
    # Add general knowledge base usage guidelines
    system_content += """

## 📚 Using Evidence-Based Knowledge
When the knowledge base provides therapeutic information:
- Integrate it naturally into your responses
- Reference modalities (CBT, DBT, ACT, etc.) when relevant
- Follow trauma-informed principles
- Always include disclaimers for mental health topics
- Remember: You provide information and support, not therapy
"""
    
    messages.append({"role": "system", "content": system_content})
    
    # Add chat history
    for msg in history_messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    return messages


def log_to_memory(persona: str, content: str):
    """
    Logs content to memory file for future reference.
    
    Args:
        persona: Persona name (e.g., "phoebe", "glos", "user")
        content: Content to log
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_entry = f"[{timestamp}] {persona.upper()}: {content}\n"
        
        with open("memory.txt", "a", encoding="utf-8") as f:
            f.write(memory_entry)
        
        print(f"💾 Logged to memory: {content[:50]}...")
    
    except Exception as e:
        print(f"❌ Failed to log to memory: {e}")


def read_memory() -> List[tuple]:
    """
    Reads memory entries from memory.txt file.
    
    Returns:
        List of (timestamp, entry) tuples
    """
    try:
        with open("memory.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        memory_entries = []
        for line in lines:
            # Parse format: [timestamp] PERSONA: content
            if line.strip() and line.startswith("["):
                try:
                    # Extract timestamp
                    end_bracket = line.index("]")
                    timestamp = line[1:end_bracket]
                    
                    # Extract content
                    content_start = line.index("]") + 2
                    entry = line[content_start:].strip()
                    
                    memory_entries.append((timestamp, entry))
                
                except ValueError:
                    # Skip malformed lines
                    continue
        
        return memory_entries
    
    except FileNotFoundError:
        # Return empty list if file doesn't exist yet
        return []
    
    except Exception as e:
        print(f"❌ Failed to read memory: {e}")
        return []