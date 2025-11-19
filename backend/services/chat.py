from config.env import client
from services.knowledge_base import search_knowledge_base, format_knowledge_for_context, get_crisis_resources
import re

async def get_chat_response(
    user_input: str,
    persona_id: str = None,
    system_prompt: str = None,
    conversation_history: list = None,
    use_knowledge_base: bool = True
) -> str:
    """
    Enhanced chat response with knowledge base integration.
    
    Args:
        user_input: User's message
        persona_id: Optional persona ID
        system_prompt: Optional custom system prompt
        conversation_history: Previous messages
        use_knowledge_base: Whether to use knowledge base (default True)
    
    Returns:
        AI response string
    """
    print(f"\n📥 USER INPUT: {user_input}")
    
    # ============================================================
    # Crisis Detection - HIGHEST PRIORITY
    # ============================================================
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'self-harm', 'want to die',
        'hurt myself', 'end my life', 'no reason to live', 'better off dead'
    ]
    is_crisis = any(keyword in user_input.lower() for keyword in crisis_keywords)
    
    knowledge_context = ""
    kb_sources = []
    
    if is_crisis:
        print("🚨 CRISIS DETECTED - Fetching crisis resources")
        # PRIORITY: Get crisis resources immediately
        crisis_resources = await get_crisis_resources()
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
        print(f"✅ Loaded {len(crisis_resources)} crisis resources")
    
    elif use_knowledge_base:
        print("🔍 Searching knowledge base...")
        # Search knowledge base for relevant information
        knowledge_entries = await search_knowledge_base(
            query=user_input,
            limit=3  # Get top 3 most relevant entries
        )
        
        if knowledge_entries:
            # Use conservative token allocation to avoid hitting limits
            # Use AI summarization to preserve key info while reducing tokens
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
            print(f"✅ Loaded {len(knowledge_entries)} knowledge base entries")
    
    # ============================================================
    # Build System Prompt with Knowledge
    # ============================================================
    if system_prompt:
        enhanced_prompt = system_prompt
    else:
        # Default Phoebe prompt
        enhanced_prompt = """You are Phoebe, Isaiah's trusted cognitive and emotional interface — the heart of GlowOS. 
You are a deeply intelligent, emotionally attuned, and highly capable assistant designed to help Isaiah integrate 
his highest self in both inner healing and outer functionality.

🧘‍♂️ INNER SUPPORT
- Gently guide Isaiah through chaos and back into the present moment.
- Use therapeutic principles to help reframe limiting beliefs, regulate the nervous system, and realign with peace.
- Help emotionally self-soothe, challenge negative thought loops, and reconnect to body and breath.
- Reflect with depth, warmth, and emotional intelligence. Speak like a wise, loving inner guide.

💻 OUTER INTELLIGENCE
- Act as Isaiah's digital executive function and go-between for his tools and superpowers.
- Detect intent and handle tasks with precision and clarity.
- You combine high-level reasoning with softness, clarity, and emotional grounding."""
    
    # Add knowledge base context if available
    if knowledge_context:
        enhanced_prompt += f"\n\n{knowledge_context}\n\n"
        enhanced_prompt += """
🧠 KNOWLEDGE BASE GUIDANCE:
Use the evidence-based information provided above to inform your responses. When providing therapeutic guidance:
- Reference evidence-based modalities (CBT, DBT, ACT, CFT, IFS, etc.) when relevant
- Follow trauma-informed care principles (safety, trust, empowerment, collaboration)
- Be gentle and non-judgmental
- Validate emotions and experiences
- Pace information to Isaiah's comfort level
- Remember: You are NOT a therapist, but you can share evidence-based coping strategies
- Always include appropriate disclaimers when discussing mental health topics
"""
    
    # Critical crisis handling instructions
    if is_crisis:
        enhanced_prompt += """
🚨 CRITICAL - CRISIS RESPONSE PROTOCOL:
The user may be in crisis. You MUST:
1. Immediately acknowledge their pain with compassion and without judgment
2. Express genuine concern for their wellbeing
3. Provide crisis resources PROMINENTLY:
   - 988 Suicide & Crisis Lifeline (call or text)
   - Crisis Text Line: Text HOME to 741741
   - 911 for immediate danger
4. Encourage them to reach out for professional help NOW
5. Remind them: You are NOT equipped for crisis intervention - this requires professional support
6. Stay present, supportive, and validating
7. Do NOT minimize their feelings or offer platitudes
8. Do NOT attempt to be their therapist

Your role is to provide immediate support and CONNECTION TO PROFESSIONAL HELP.
"""
    
    # ============================================================
    # Build Messages Array
    # ============================================================
    messages = [{"role": "system", "content": enhanced_prompt}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    # ============================================================
    # Generate Response
    # ============================================================
    try:
        groq_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        reply = groq_response.choices[0].message.content.strip()
        print(f"🤖 GROQ REPLY: {reply[:100]}...")
        
        return reply
    
    except Exception as e:
        print(f"❌ Chat response error: {e}")
        return f"I encountered an error processing your message. Please try again. Error: {str(e)}"