"""Task control endpoints"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from glowos.glow_state import glow_state_store

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/{task_id}/stop")
async def stop_task(task_id: str):
    """Stop a running task"""
    state = glow_state_store.get_state()
    task_found = False
    
    for task in state.tasks.active:
        if task.id == task_id:
            task.status = "error"
            task.message = "Stopped by user"
            task_found = True
            break
    
    if not task_found:
        raise HTTPException(status_code=404, detail="Task not found")
    
    glow_state_store.replace(state)
    return {"success": True, "message": "Task stopped"}

@router.post("/{task_id}/restart")
async def restart_task(task_id: str):
    """Restart a task"""
    state = glow_state_store.get_state()
    task_found = None
    
    # Find task in active or recent
    for task in state.tasks.active:
        if task.id == task_id:
            task_found = task
            break
    
    if not task_found:
        for task in state.tasks.recent:
            if task.id == task_id:
                task_found = task
                break
    
    if not task_found:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create new task with same type
    from glowos.glow_state import TaskInfo
    from datetime import datetime
    
    new_task = TaskInfo(
        id=task_found.id,  # Keep same ID for tracking
        type=task_found.type,
        status="running",
        progress=0.0,
        started_at=datetime.utcnow()
    )
    
    # Remove old task, add new one
    state.tasks.active = [t for t in state.tasks.active if t.id != task_id]
    state.tasks.active.append(new_task)
    
    glow_state_store.replace(state)
    return {"success": True, "message": "Task restarted"}

