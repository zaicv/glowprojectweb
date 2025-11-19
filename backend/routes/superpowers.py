# ============================================
# 🦸 Superpowers Routes
# ============================================
# All HTTP endpoints related to superpowers execution and management

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio

router = APIRouter(prefix="/api/superpowers", tags=["superpowers"])

# This will be set by main.py via set_superpowers()
SUPERPOWERS: Dict[str, Any] = {}

def set_superpowers(superpowers_dict: Dict[str, Any]):
    """Inject loaded superpowers from main.py"""
    global SUPERPOWERS
    SUPERPOWERS = superpowers_dict
    print(f"✅ Superpowers router initialized with {len(SUPERPOWERS)} powers")


# =========================
# GET: List All Superpowers
# =========================

@router.get("/test", response_class=JSONResponse)
async def test_superpowers():
    """Simple test endpoint to debug superpowers loading"""
    try:
        print(f"🔍 SUPERPOWERS dict type: {type(SUPERPOWERS)}")
        print(f"🔍 SUPERPOWERS keys: {list(SUPERPOWERS.keys())}")
        print(f"🔍 SUPERPOWERS length: {len(SUPERPOWERS)}")
        
        powers_info = []
        for key, power in SUPERPOWERS.items():
            try:
                power_info = {
                    "key": key,
                    "name": getattr(power, 'name', 'Unknown'),
                    "has_intent_map": hasattr(power, 'intent_map'),
                    "intent_count": len(getattr(power, 'intent_map', {}))
                }
                powers_info.append(power_info)
                print(f"✅ Successfully processed power: {key}")
            except Exception as e:
                print(f"❌ Error processing power {key}: {e}")
                powers_info.append({
                    "key": key,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "superpowers_loaded": len(SUPERPOWERS),
            "powers_info": powers_info
        }
        
    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Test failed: {str(e)}"}
        )


@router.get("", response_class=JSONResponse)
async def get_available_superpowers():
    """Returns a list of all available superpowers and their capabilities"""
    try:
        print(f"🔍 Starting superpowers endpoint...")
        print(f"🔍 SUPERPOWERS available: {len(SUPERPOWERS)}")
        
        superpowers_info = []
        
        for power_name, power_instance in SUPERPOWERS.items():
            try:
                print(f"🔍 Processing power: {power_name}")
                
                superpower_data = {
                    "name": getattr(power_instance, 'name', power_name),
                    "key": power_name,
                    "intents": {}
                }
                
                # Get the intent map if it exists
                if hasattr(power_instance, 'intent_map'):
                    superpower_data["intents"] = power_instance.intent_map
                    print(f"✅ Added {len(power_instance.intent_map)} intents for {power_name}")
                else:
                    print(f"⚠️ No intent_map found for {power_name}")
                
                # Add any additional metadata if available
                if hasattr(power_instance, 'description'):
                    superpower_data["description"] = power_instance.description
                    
                superpowers_info.append(superpower_data)
                print(f"✅ Successfully added {power_name}")
                
            except Exception as e:
                print(f"❌ Error processing {power_name}: {e}")
                superpowers_info.append({
                    "name": power_name,
                    "key": power_name,
                    "error": str(e),
                    "intents": {}
                })
        
        result = {
            "superpowers": superpowers_info,
            "count": len(superpowers_info),
            "message": f"Found {len(superpowers_info)} available superpowers"
        }
        
        print(f"✅ Returning result with {len(superpowers_info)} superpowers")
        return result
        
    except Exception as e:
        print(f"❌ Critical error in superpowers endpoint: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500, 
            content={"error": f"Failed to retrieve superpowers: {str(e)}"}
        )


# =========================
# GET: Single Superpower Details
# =========================

@router.get("/{superpower_name}", response_class=JSONResponse)
async def get_superpower_details(superpower_name: str):
    """Get detailed information about a specific superpower"""
    try:
        # Try to find the superpower by name or key
        power_instance = None
        power_key = None
        
        for key, instance in SUPERPOWERS.items():
            if key == superpower_name or instance.name.lower() == superpower_name.lower():
                power_instance = instance
                power_key = key
                break
        
        if not power_instance:
            return JSONResponse(
                status_code=404,
                content={"error": f"Superpower '{superpower_name}' not found"}
            )
        
        superpower_data = {
            "name": power_instance.name,
            "key": power_key,
            "intents": getattr(power_instance, 'intent_map', {}),
            "description": getattr(power_instance, 'description', None),
            "methods": []
        }
        
        # Get available methods (optional - for debugging)
        methods = [method for method in dir(power_instance) 
                  if not method.startswith('_') and callable(getattr(power_instance, method))]
        superpower_data["methods"] = methods
        
        return superpower_data
        
    except Exception as e:
        print(f"❌ Error getting superpower details: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get superpower details: {str(e)}"}
        )


# =========================
# POST: Execute Superpower Intent
# =========================

@router.post("/{superpower_name}/execute", response_class=JSONResponse)
async def execute_superpower_direct(superpower_name: str, request: Request):
    """Direct execution of superpower intents without going through Mistral"""
    try:
        data = await request.json()
        intent = data.get("intent")
        kwargs = data.get("kwargs", {})
        
        if not intent:
            return JSONResponse(
                status_code=400,
                content={"error": "Intent is required"}
            )
        
        # Find the superpower
        power_instance = None
        for key, instance in SUPERPOWERS.items():
            if key == superpower_name or instance.name.lower() == superpower_name.lower():
                power_instance = instance
                break
        
        if not power_instance:
            return JSONResponse(
                status_code=404,
                content={"error": f"Superpower '{superpower_name}' not found"}
            )
        
        # Check if the intent exists
        if intent not in power_instance.intent_map:
            return JSONResponse(
                status_code=400,
                content={"error": f"Intent '{intent}' not found in {superpower_name}"}
            )
        
        # Execute the intent directly
        result = await power_instance.run(intent, **kwargs)
        
        return {"result": result, "intent": intent, "superpower": superpower_name}
        
    except Exception as e:
        print(f"❌ Error executing superpower: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to execute: {str(e)}"}
        )