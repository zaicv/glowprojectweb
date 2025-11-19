"""
🧠 Consciousness Routes
Handles consciousness state analysis and retrieval
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel

from services.consciousness_tracker import analyze_and_save_state, analyze_consciousness_state
from config.env import supabase

router = APIRouter(prefix="/api/consciousness", tags=["consciousness"])


class AnalyzeRequest(BaseModel):
    message: str
    user_id: str
    thread_id: Optional[str] = None
    message_id: Optional[str] = None
    context: Optional[str] = None


class GetStatesRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 100
    start_time: Optional[str] = None
    state_type: Optional[str] = None  # 'chaos', 'glow', 'neutral', or None for all


@router.post("/analyze", response_class=JSONResponse)
async def analyze_message(request: AnalyzeRequest):
    """
    Analyze a message to determine consciousness state (Chaos vs Glow)
    Saves the state to the database and returns the analysis
    """
    try:
        result = await analyze_and_save_state(
            message_text=request.message,
            user_id=request.user_id,
            thread_id=request.thread_id,
            message_id=request.message_id,
            context=request.context
        )
        
        return JSONResponse(content={
            "success": True,
            "state": result
        })
    except Exception as e:
        print(f"❌ Error analyzing consciousness state: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/analyze-only", response_class=JSONResponse)
async def analyze_only(request: AnalyzeRequest):
    """
    Analyze a message without saving to database (for testing/preview)
    """
    try:
        result = await analyze_consciousness_state(
            message_text=request.message,
            user_id=request.user_id,
            thread_id=request.thread_id,
            message_id=request.message_id,
            context=request.context
        )
        
        return JSONResponse(content={
            "success": True,
            "state": result
        })
    except Exception as e:
        print(f"❌ Error analyzing consciousness state: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/states/{user_id}", response_class=JSONResponse)
async def get_user_states(
    user_id: str,
    limit: int = 100,
    start_time: Optional[str] = None,
    state_type: Optional[str] = None
):
    """
    Get consciousness states for a user
    """
    try:
        query = supabase.table("consciousness_states")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=True)\
            .limit(limit)
        
        if start_time:
            query = query.gte("timestamp", start_time)
        
        if state_type and state_type in ['chaos', 'glow', 'neutral']:
            query = query.eq("state_type", state_type)
        
        result = query.execute()
        states = getattr(result, "data", [])
        
        return JSONResponse(content={
            "success": True,
            "states": states,
            "count": len(states)
        })
    except Exception as e:
        print(f"❌ Error fetching consciousness states: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/statistics/{user_id}", response_class=JSONResponse)
async def get_statistics(
    user_id: str,
    days: int = 30
):
    """
    Get consciousness statistics for a user over a time period
    """
    try:
        start_time = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Use the SQL function we created
        result = supabase.rpc(
            "get_consciousness_statistics",
            {
                "p_user_id": user_id,
                "p_start_time": start_time
            }
        ).execute()
        
        stats = getattr(result, "data", [])
        
        if stats and len(stats) > 0:
            return JSONResponse(content={
                "success": True,
                "statistics": stats[0]
            })
        else:
            return JSONResponse(content={
                "success": True,
                "statistics": {
                    "total_states": 0,
                    "chaos_count": 0,
                    "glow_count": 0,
                    "neutral_count": 0,
                    "avg_intensity": 0.5,
                    "avg_sentiment": 0.0,
                    "chaos_percentage": 0.0,
                    "glow_percentage": 0.0
                }
            })
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/current/{user_id}", response_class=JSONResponse)
async def get_current_state(user_id: str):
    """
    Get the most recent consciousness state for a user
    """
    try:
        result = supabase.table("consciousness_states")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=True)\
            .limit(1)\
            .execute()
        
        states = getattr(result, "data", [])
        
        if states and len(states) > 0:
            return JSONResponse(content={
                "success": True,
                "state": states[0]
            })
        else:
            return JSONResponse(content={
                "success": True,
                "state": None,
                "message": "No states found for this user"
            })
    except Exception as e:
        print(f"❌ Error fetching current state: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/timeline/{user_id}", response_class=JSONResponse)
async def get_timeline(
    user_id: str,
    days: int = 7,
    interval: str = "hour"  # 'hour', 'day', 'week'
):
    """
    Get aggregated timeline data for visualization
    Returns states grouped by time interval
    """
    try:
        start_time = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get all states in the time range
        result = supabase.table("consciousness_states")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("timestamp", start_time)\
            .order("timestamp", desc=False)\
            .execute()
        
        states = getattr(result, "data", [])
        
        # Group by interval
        timeline_data = []
        current_interval = None
        interval_states = []
        
        for state in states:
            state_time = datetime.fromisoformat(state["timestamp"].replace("Z", "+00:00"))
            
            # Determine interval bucket
            if interval == "hour":
                interval_key = state_time.replace(minute=0, second=0, microsecond=0)
            elif interval == "day":
                interval_key = state_time.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # week
                days_since_monday = state_time.weekday()
                interval_key = (state_time - timedelta(days=days_since_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            
            if current_interval != interval_key:
                if current_interval is not None and interval_states:
                    # Calculate averages for previous interval
                    avg_intensity = sum(s["intensity"] for s in interval_states) / len(interval_states)
                    avg_sentiment = sum(s.get("sentiment_score", 0) for s in interval_states) / len(interval_states)
                    chaos_count = sum(1 for s in interval_states if s["state_type"] == "chaos")
                    glow_count = sum(1 for s in interval_states if s["state_type"] == "glow")
                    neutral_count = sum(1 for s in interval_states if s["state_type"] == "neutral")
                    
                    timeline_data.append({
                        "timestamp": current_interval.isoformat(),
                        "avg_intensity": avg_intensity,
                        "avg_sentiment": avg_sentiment,
                        "chaos_count": chaos_count,
                        "glow_count": glow_count,
                        "neutral_count": neutral_count,
                        "total_count": len(interval_states)
                    })
                
                current_interval = interval_key
                interval_states = []
            
            interval_states.append(state)
        
        # Handle last interval
        if current_interval is not None and interval_states:
            avg_intensity = sum(s["intensity"] for s in interval_states) / len(interval_states)
            avg_sentiment = sum(s.get("sentiment_score", 0) for s in interval_states) / len(interval_states)
            chaos_count = sum(1 for s in interval_states if s["state_type"] == "chaos")
            glow_count = sum(1 for s in interval_states if s["state_type"] == "glow")
            neutral_count = sum(1 for s in interval_states if s["state_type"] == "neutral")
            
            timeline_data.append({
                "timestamp": current_interval.isoformat(),
                "avg_intensity": avg_intensity,
                "avg_sentiment": avg_sentiment,
                "chaos_count": chaos_count,
                "glow_count": glow_count,
                "neutral_count": neutral_count,
                "total_count": len(interval_states)
            })
        
        return JSONResponse(content={
            "success": True,
            "timeline": timeline_data,
            "interval": interval,
            "days": days
        })
    except Exception as e:
        print(f"❌ Error fetching timeline: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

