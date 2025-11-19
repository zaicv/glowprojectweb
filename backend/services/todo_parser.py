from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import re
import json
from ollama import chat as mistral_chat




# =======================================================
# 📝 TODO PARSING WITH LOCAL MISTRAL
# =======================================================
# region

class TodoParseRequest(BaseModel):
    rawTask: str
    availableGroups: List[str]

class ParsedTodo(BaseModel):
    title: str
    description: Optional[str] = None
    goal_group: str
    priority: int  # 1=high, 2=medium, 3=low
    deadline: Optional[str] = None  # ISO format date

async def parse_todo_with_mistral(request: TodoParseRequest):
    """
    Use local Ollama Mistral to intelligently parse a natural language todo into structured data
    """
    try:
        print(f"🤖 Parsing todo: {request.rawTask}")
        print(f"📋 Available groups: {request.availableGroups}")
        
        # Create the prompt for Mistral
        system_prompt = f"""You are a smart todo parser. Parse the user's natural language todo into structured data.

AVAILABLE GOAL GROUPS: {', '.join(request.availableGroups)}

Your task:
1. Extract a clean, actionable title (start with a verb when possible)
2. Determine which goal group fits best (MUST be from the available list)
3. Set priority: 1=urgent/important, 2=normal, 3=low priority
4. Extract deadline if mentioned (convert to ISO date format YYYY-MM-DDTHH:MM:SSZ)
5. Add helpful description if context is useful

RULES:
- goal_group MUST be exactly one of the available groups
- If no clear match, use "General"
- Priority should reflect urgency and importance
- Only set deadline if explicitly or implicitly mentioned
- Keep title concise and actionable (under 80 characters)
- Respond ONLY with valid JSON, no other text

Current date context: {datetime.now().strftime('%Y-%m-%d')} (use for relative dates like "tomorrow", "next week")

Examples:
{{
  "title": "Buy groceries for fish tacos",
  "description": "Need ingredients for fish tacos this week",
  "goal_group": "Adapt My Diet",
  "priority": 2,
  "deadline": "2024-12-31T23:59:59Z"
}}

{{
  "title": "Call mom about dinner plans",
  "description": null,
  "goal_group": "Family", 
  "priority": 2,
  "deadline": "2024-12-25T18:00:00Z"
}}"""

        user_prompt = f"Parse this todo: {request.rawTask}"
        
        # Call your local Mistral with timeout handling
        try:
            mistral_response = mistral_chat(
                model="mistral",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.1}  # Lower temperature for more consistent parsing
            )
            
            # Extract content from Ollama response
            raw_content = mistral_response["message"]["content"]
            print(f"🧠 Mistral raw response: {raw_content}")
            
        except Exception as e:
            print(f"❌ Mistral API error: {e}")
            # Fall back immediately to heuristic parsing
            parsed_data = extract_fallback_data(request.rawTask, request.availableGroups)
            return validate_parsed_todo(parsed_data, request.availableGroups)
        
        # Parse the JSON response with better error handling
        try:
            # Clean the response - extract JSON even if wrapped in other text
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
            else:
                json_content = raw_content
                
            parsed_data = json.loads(json_content)
            print(f"🎯 Parsed JSON: {parsed_data}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"❌ Raw content: {raw_content}")
            # Fallback parsing if JSON is malformed
            parsed_data = extract_fallback_data(request.rawTask, request.availableGroups)
        
        # Validate and clean the data
        validated_todo = validate_parsed_todo(parsed_data, request.availableGroups)
        
        print(f"✅ Validated todo: {validated_todo}")
        return validated_todo
        
    except Exception as e:
        print(f"❌ Error parsing todo: {e}")
        # Return fallback data
        return {
            "title": request.rawTask[:80].strip(),  # Truncate to reasonable length
            "description": None,
            "goal_group": request.availableGroups[0] if request.availableGroups else "General",
            "priority": 2,
            "deadline": None
        }

def extract_fallback_data(raw_task: str, available_groups: List[str]) -> dict:
    """
    Enhanced fallback parser using simple heuristics if Mistral fails
    """
    print("🔄 Using fallback parsing...")
    
    task_lower = raw_task.lower()
    goal_group = available_groups[0] if available_groups else "General"  # default to first available
    
    # Enhanced keyword matching - map to your exact group names
    group_keywords = {
        "Adapt My Diet": ["grocery", "groceries", "cook", "cooking", "eat", "eating", "food", "meal", "diet", "nutrition", "taco", "recipe", "shopping", "shop", "kitchen"],
        "Physical Reconditioning": ["workout", "gym", "exercise", "run", "running", "jog", "lift", "lifting", "cardio", "weight", "weights", "muscle", "protein", "fitness", "train", "training"],
        "Family": ["mom", "dad", "family", "parent", "parents", "sibling", "call", "visit", "family"],
        "Ava": ["ava"],
        "House": ["clean", "cleaning", "wash", "washing", "vacuum", "organize", "fix", "repair", "bathroom", "kitchen", "home", "house", "chore", "chores"],
        "College / Career": ["work", "job", "career", "application", "apply", "resume", "interview", "college", "school", "study", "homework"],
        "Money + Admin": ["pay", "bill", "bills", "money", "bank", "banking", "budget", "finance", "financial", "tax", "taxes", "admin", "paperwork"]
    }
    
    # Find best matching group
    best_match_score = 0
    best_group = goal_group
    
    for group_name, keywords in group_keywords.items():
        if group_name in available_groups:
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > best_match_score:
                best_match_score = score
                best_group = group_name
    
    goal_group = best_group
    
    # Enhanced deadline extraction
    deadline = None
    today = datetime.now()
    
    # More comprehensive date patterns
    if any(word in task_lower for word in ["today", "this evening", "tonight"]):
        deadline = today.replace(hour=23, minute=59, second=59).isoformat() + "Z"
    elif "tomorrow" in task_lower:
        deadline = (today + timedelta(days=1)).replace(hour=23, minute=59, second=59).isoformat() + "Z"
    elif any(phrase in task_lower for phrase in ["this week", "by friday", "end of week"]):
        # Find next Friday
        days_ahead = 4 - today.weekday()  # Friday is 4
        if days_ahead <= 0:
            days_ahead += 7
        deadline = (today + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=59).isoformat() + "Z"
    elif "next week" in task_lower:
        deadline = (today + timedelta(days=7)).replace(hour=23, minute=59, second=59).isoformat() + "Z"
    elif "this month" in task_lower:
        # End of current month
        next_month = today.replace(day=28) + timedelta(days=4)
        deadline = (next_month - timedelta(days=next_month.day)).replace(hour=23, minute=59, second=59).isoformat() + "Z"
    
    # Enhanced priority detection
    priority = 2  # default medium
    urgent_words = ["urgent", "asap", "immediately", "emergency", "important", "critical", "now", "today"]
    low_words = ["someday", "eventually", "maybe", "consider", "when i have time", "low priority"]
    
    if any(word in task_lower for word in urgent_words):
        priority = 1
    elif any(word in task_lower for word in low_words):
        priority = 3
    
    # Clean up title - make it more actionable
    title = raw_task.strip()
    if len(title) > 80:
        title = title[:77] + "..."
    
    # Try to make title start with action verb if it doesn't already
    action_verbs = ["buy", "call", "email", "schedule", "book", "research", "find", "clean", "organize", "pay", "submit", "complete", "finish", "start"]
    if not any(title.lower().startswith(verb) for verb in action_verbs):
        # This is a simple heuristic - you might want to make it more sophisticated
        if "grocery" in task_lower or "shopping" in task_lower:
            if not title.lower().startswith("buy"):
                title = "Buy " + title.lower()
        elif any(word in task_lower for word in ["mom", "dad", "family"]) and "call" not in task_lower:
            title = "Call " + title
    
    return {
        "title": title,
        "description": None,
        "goal_group": goal_group,
        "priority": priority,
        "deadline": deadline
    }

def validate_parsed_todo(data: dict, available_groups: List[str]) -> dict:
    """
    Enhanced validation and cleaning of parsed todo data
    """
    # Ensure goal_group is valid
    if data.get("goal_group") not in available_groups:
        print(f"⚠️ Invalid goal_group '{data.get('goal_group')}', using fallback")
        # Try to find closest match or use first available
        data["goal_group"] = available_groups[0] if available_groups else "General"
    
    # Ensure priority is valid
    priority = data.get("priority", 2)
    if priority not in [1, 2, 3]:
        priority = 2
    
    # Clean title - ensure it's not empty and reasonable length
    title = data.get("title", "").strip()
    if not title:
        title = "Untitled Task"
    elif len(title) > 100:
        title = title[:97] + "..."
    
    # Clean description 
    description = data.get("description")
    if description and len(description.strip()) == 0:
        description = None
    elif description and len(description) > 500:
        description = description[:497] + "..."
    
    # Validate deadline format
    deadline = data.get("deadline")
    if deadline:
        try:
            # Ensure proper Z suffix for UTC
            if not deadline.endswith('Z'):
                deadline += 'Z'
            # Validate by parsing
            datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        except Exception as e:
            print(f"⚠️ Invalid deadline format: {deadline}, error: {e}")
            deadline = None
    
    return {
        "title": title,
        "description": description,
        "goal_group": data["goal_group"],
        "priority": priority,
        "deadline": deadline
    }
