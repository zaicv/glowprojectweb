from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import asyncio

# import your download function here

router = APIRouter()

progress_dict = {}


class DownloadRequest(BaseModel):
    url: str
    quality: str = "720"
    format_: str = "mp4"
    audio_quality: str = "192"
    save_thumbnail: bool = False
    output_dir: str = "/Users/zai/Desktop/plex/Podcasts"
    filename_suffix: str = ""

@router.post("/download")
def download_video(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        background_download_video,
        request.url,
        request.quality,
        request.format_,
        request.audio_quality,
        request.save_thumbnail,
        request.output_dir,
        request.filename_suffix,
    )
    return {"status": "Download started"}

@router.get("/download")
async def download_video_from_url(url: str, format: str = "mp4"):
    try:
        command = f"yt-dlp -f {format} {url} -o ~/Downloads/%(title)s.%(ext)s"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return f"✅ Download started for: {url}"
        else:
            return f"❌ Error during download: {stderr.decode()}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"
    

@router.get("/progress")
async def get_progress(url: str = Query(...)):
    video_id = extract_video_id(url)
    if not video_id:
        return JSONResponse({"error": "Invalid YouTube URL"}, status_code=400)

    data = progress_dict.get(video_id, {})
    total = data.get("total_bytes", 0) or 1
    downloaded = data.get("downloaded_bytes", 0)

    return {
        "status": data.get("status", "not_started"),
        "filename": data.get("filename"),
        "downloaded_mb": round(downloaded / 1_000_000, 2),
        "total_mb": round(total / 1_000_000, 2),
        "percent": round((downloaded / total) * 100, 2),
        "speed": round((data.get("speed", 0) or 0) / 1_000, 2),  # kB/s
        "eta": data.get("eta"),
        "elapsed": data.get("elapsed")
    }