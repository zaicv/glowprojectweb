# routes/glow_state_routes.py
print("🔧 [GlowState] Loading glow_state_routes.py module...")

from fastapi import APIRouter, HTTPException
print("🔧 [GlowState] FastAPI imported successfully")

try:
    from glowos.glow_state import glow_state_store, GlowState
    print(f"✅ [GlowState] Successfully imported glow_state_store and GlowState")
except Exception as e:
    print(f"❌ [GlowState] Failed to import glow_state_store: {e}")
    import traceback
    traceback.print_exc()
    raise

import traceback

print("🔧 [GlowState] Creating APIRouter with prefix='/glow'...")
router = APIRouter(prefix="/glow", tags=["glow"])
print(f"✅ [GlowState] Router created: {router}")
print(f"✅ [GlowState] Router prefix: {router.prefix}")

@router.get("/state", response_model=GlowState)
async def get_glow_state():
    """Get the current GlowState from the store."""
    print(f"🌐 [GlowState] GET /glow/state endpoint called")
    try:
        state = glow_state_store.get_state()
        print(f"✅ [GlowState] Returning state: system.cpu={state.system.cpu_usage:.2%}, runtime.backend={state.runtime.backend_running}")
        return state
    except Exception as e:
        error_msg = f"❌ [GlowState] Error getting state: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get GlowState: {str(e)}")

@router.post("/notifications/clear")
async def clear_notifications():
    """Clear disc insertion notification"""
    try:
        glow_state_store.update(notifications={"disc_inserted": False, "disc_path": None, "timestamp": None})
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print(f"✅ [GlowState] Route /state registered. Total routes in router: {len(router.routes)}")
for route in router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  - Route: {list(route.methods)} {route.path}")