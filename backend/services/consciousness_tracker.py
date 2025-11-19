"""
🧠 Consciousness Tracker Service
Analyzes messages to detect Chaos vs Glow states based on The Glow philosophy
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from config.env import supabase


# Chaos indicators - patterns that suggest egoic mind, fear, control, survival-based patterns
CHAOS_INDICATORS = {
    "anxiety_words": [
        "anxious", "worried", "stress", "panic", "fear", "afraid", "scared",
        "overwhelmed", "stressed", "nervous", "tense", "frightened", "terrified",
        "dread", "apprehensive", "uneasy", "restless", "agitated"
    ],
    "self_doubt": [
        "doubt", "unsure", "uncertain", "confused", "don't know", "can't decide",
        "second guess", "hesitant", "insecure", "inadequate", "not good enough",
        "failure", "failing", "failed", "mistake", "wrong", "stupid", "idiot"
    ],
    "perfectionism": [
        "perfect", "must be", "should be", "have to", "need to", "must",
        "should", "ought", "imperfect", "flawed", "not right", "not enough",
        "more", "better", "improve", "fix", "correct"
    ],
    "control_fear": [
        "control", "controlled", "controlling", "manage", "manageable",
        "handle", "can't handle", "can't deal", "too much", "can't cope",
        "lose control", "out of control", "chaos", "messy", "disorder"
    ],
    "looping_thoughts": [
        "keep thinking", "can't stop", "can't get out", "stuck", "trapped",
        "repeating", "going in circles", "same thought", "over and over",
        "ruminating", "obsessing", "fixating", "dwelling"
    ],
    "negation": [
        "can't", "won't", "don't", "never", "nothing", "nobody", "nowhere",
        "impossible", "hopeless", "pointless", "useless", "worthless"
    ]
}

# Glow indicators - patterns that suggest presence, awareness, peace, acceptance
GLOW_INDICATORS = {
    "presence": [
        "present", "aware", "awareness", "notice", "noticing", "observing",
        "witnessing", "witness", "conscious", "consciousness", "mindful",
        "mindfulness", "here", "now", "moment", "present moment"
    ],
    "peace_acceptance": [
        "peace", "peaceful", "calm", "calmness", "serene", "tranquil",
        "accept", "accepting", "acceptance", "okay", "fine", "alright",
        "let it be", "let go", "release", "surrender", "trust", "trusting"
    ],
    "awareness": [
        "aware", "awareness", "conscious", "consciousness", "see", "seeing",
        "understand", "understand", "clarity", "clear", "illuminated",
        "light", "enlightened", "awakened", "awake"
    ],
    "grounding": [
        "grounded", "centered", "balanced", "stable", "steady", "solid",
        "breath", "breathing", "body", "sensation", "feel", "feeling",
        "touch", "sense", "senses"
    ],
    "compassion": [
        "compassion", "compassionate", "kind", "kindness", "gentle",
        "loving", "love", "care", "caring", "tender", "soft", "warm",
        "understanding", "empathy", "empathetic"
    ],
    "freedom": [
        "free", "freedom", "liberated", "liberation", "release", "released",
        "unbound", "unburdened", "light", "lightness", "ease", "easy",
        "flow", "flowing", "natural", "spontaneous"
    ]
}


def normalize_text(text: str) -> str:
    """Normalize text for analysis"""
    if not text:
        return ""
    # Convert to lowercase and remove extra whitespace
    text = text.lower().strip()
    # Remove special characters but keep words
    text = re.sub(r'[^\w\s]', ' ', text)
    return text


def count_indicators(text: str, indicator_list: List[str]) -> int:
    """Count how many indicator words appear in the text"""
    normalized = normalize_text(text)
    count = 0
    for indicator in indicator_list:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(indicator.lower()) + r'\b'
        if re.search(pattern, normalized):
            count += 1
    return count


def detect_chaos_indicators(text: str) -> Tuple[int, List[str]]:
    """Detect Chaos indicators in text and return count and list of found indicators"""
    found_indicators = []
    total_count = 0
    
    for category, indicators in CHAOS_INDICATORS.items():
        count = count_indicators(text, indicators)
        if count > 0:
            total_count += count
            found_indicators.extend([indicator for indicator in indicators 
                                   if re.search(r'\b' + re.escape(indicator.lower()) + r'\b', 
                                               normalize_text(text))])
    
    return total_count, found_indicators[:10]  # Limit to 10 most relevant


def detect_glow_indicators(text: str) -> Tuple[int, List[str]]:
    """Detect Glow indicators in text and return count and list of found indicators"""
    found_indicators = []
    total_count = 0
    
    for category, indicators in GLOW_INDICATORS.items():
        count = count_indicators(text, indicators)
        if count > 0:
            total_count += count
            found_indicators.extend([indicator for indicator in indicators 
                                   if re.search(r'\b' + re.escape(indicator.lower()) + r'\b', 
                                               normalize_text(text))])
    
    return total_count, found_indicators[:10]  # Limit to 10 most relevant


def calculate_sentiment_score(text: str, chaos_count: int, glow_count: int) -> float:
    """
    Calculate sentiment score from -1 (strong chaos) to 1 (strong glow)
    """
    if not text or len(text.strip()) < 10:
        return 0.0
    
    # Base score from indicator counts
    total_indicators = chaos_count + glow_count
    if total_indicators == 0:
        return 0.0
    
    # Calculate ratio
    score = (glow_count - chaos_count) / max(total_indicators, 1)
    
    # Normalize to -1 to 1 range
    return max(-1.0, min(1.0, score))


def determine_state_type(chaos_count: int, glow_count: int, sentiment_score: float) -> str:
    """
    Determine state type based on indicator counts and sentiment
    Returns 'chaos', 'glow', or 'neutral'
    """
    # If significant difference in counts, use that
    if chaos_count > glow_count * 2:
        return 'chaos'
    elif glow_count > chaos_count * 2:
        return 'glow'
    
    # Use sentiment score as tiebreaker
    if sentiment_score < -0.3:
        return 'chaos'
    elif sentiment_score > 0.3:
        return 'glow'
    else:
        return 'neutral'


def calculate_intensity(chaos_count: int, glow_count: int, state_type: str) -> float:
    """
    Calculate intensity from 0 to 1 based on how strong the state is
    """
    total_count = chaos_count + glow_count
    
    if total_count == 0:
        return 0.5  # Neutral intensity
    
    if state_type == 'chaos':
        # Intensity increases with chaos indicators
        intensity = min(1.0, chaos_count / 10.0)  # Normalize to 0-1
        return max(0.3, intensity)  # Minimum intensity for detected chaos
    elif state_type == 'glow':
        # Intensity increases with glow indicators
        intensity = min(1.0, glow_count / 10.0)  # Normalize to 0-1
        return max(0.3, intensity)  # Minimum intensity for detected glow
    else:
        # Neutral state - intensity closer to 0.5
        return 0.5


async def analyze_consciousness_state(
    message_text: str,
    user_id: str,
    thread_id: Optional[str] = None,
    message_id: Optional[str] = None,
    context: Optional[str] = None
) -> Dict:
    """
    Analyze a message to determine consciousness state (Chaos vs Glow)
    
    Returns:
        Dict with state_type, intensity, sentiment_score, chaos_indicators, glow_indicators
    """
    if not message_text or len(message_text.strip()) < 3:
        return {
            "state_type": "neutral",
            "intensity": 0.5,
            "sentiment_score": 0.0,
            "chaos_indicators": [],
            "glow_indicators": []
        }
    
    # Detect indicators
    chaos_count, chaos_found = detect_chaos_indicators(message_text)
    glow_count, glow_found = detect_glow_indicators(message_text)
    
    # Calculate sentiment score
    sentiment_score = calculate_sentiment_score(message_text, chaos_count, glow_count)
    
    # Determine state type
    state_type = determine_state_type(chaos_count, glow_count, sentiment_score)
    
    # Calculate intensity
    intensity = calculate_intensity(chaos_count, glow_count, state_type)
    
    return {
        "state_type": state_type,
        "intensity": intensity,
        "sentiment_score": sentiment_score,
        "chaos_indicators": chaos_found,
        "glow_indicators": glow_found,
        "chaos_count": chaos_count,
        "glow_count": glow_count
    }


async def save_consciousness_state(
    user_id: str,
    state_data: Dict,
    thread_id: Optional[str] = None,
    message_id: Optional[str] = None,
    context: Optional[str] = None
) -> Optional[str]:
    """
    Save consciousness state to Supabase
    
    Returns:
        The ID of the created state record, or None if failed
    """
    try:
        state_record = {
            "user_id": user_id,
            "state_type": state_data["state_type"],
            "intensity": state_data["intensity"],
            "sentiment_score": state_data.get("sentiment_score", 0.0),
            "context": context,
            "chaos_indicators": state_data.get("chaos_indicators", []),
            "glow_indicators": state_data.get("glow_indicators", []),
            "timestamp": datetime.now().isoformat()
        }
        
        if thread_id:
            state_record["thread_id"] = thread_id
        if message_id:
            state_record["message_id"] = message_id
        
        result = supabase.table("consciousness_states").insert(state_record).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        else:
            print(f"⚠️ No data returned from consciousness_states insert")
            return None
            
    except Exception as e:
        print(f"❌ Error saving consciousness state: {e}")
        return None


async def analyze_and_save_state(
    message_text: str,
    user_id: str,
    thread_id: Optional[str] = None,
    message_id: Optional[str] = None,
    context: Optional[str] = None
) -> Dict:
    """
    Analyze message and save state in one call
    Returns the analysis result with the saved state_id
    """
    # Analyze the message
    state_data = await analyze_consciousness_state(
        message_text, user_id, thread_id, message_id, context
    )
    
    # Save to database
    state_id = await save_consciousness_state(
        user_id, state_data, thread_id, message_id, context
    )
    
    state_data["state_id"] = state_id
    return state_data

