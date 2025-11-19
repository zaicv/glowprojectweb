import subprocess
from fastapi import APIRouter, BackgroundTasks, Body, HTTPException
from fastapi.responses import JSONResponse
from superpowers.RipDisc import main as rip_core

router = APIRouter(prefix="/rip", tags=["Disc Tools"])

@router.post("/rip-disc")
async def rip_disc(background_tasks: BackgroundTasks):
    background_tasks.add_task(rip_core.process_rip)
    return JSONResponse(content={"status": "🎬 Ripping started in background"})


@router.get("/drives")
async def list_drives():
    try:
        # Don't fail on non-zero exit code
        result = subprocess.run(
            ["/Applications/MakeMKV.app/Contents/MacOS/makemkvcon", "-r", "info"],
            capture_output=True,
            text=True
        )

        drives = []
        for line in result.stdout.splitlines():
            if line.startswith("DRV:"):
                parts = line.split(",")
                drv_id = parts[0]             # DRV:0
                status_flag = int(parts[3])   # 1 = disc present, 0 = empty
                name = parts[4].strip('"')
                label = parts[5].strip('"') if len(parts) > 5 else ""
                path = parts[6].strip('"') if len(parts) > 6 else ""

                drives.append({
                    "id": drv_id,
                    "name": name,
                    "label": label,
                    "path": path,
                    "has_disc": bool(status_flag)
                })

        return {"drives": drives}

    except Exception as e:
        # Generic fallback if something unexpected happens
        return {"error": str(e)}

@router.post("/manual-metadata")
async def manual_metadata(
    filename: str = Body(...),
    manual_title: str = Body(...)
):
    result = await rip_core.process_manual_metadata(filename, manual_title)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result)