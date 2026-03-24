from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from services.ytdlp import download_audio
import uuid
import time

router = APIRouter()

# In-memory job store (swap for Redis/DB in prod)
_jobs: dict[str, dict] = {}


class DownloadRequest(BaseModel):
    video_id: str
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


def _run_download(job_id: str, req: DownloadRequest):
    _jobs[job_id]["status"] = "downloading"
    try:
        result = download_audio(
            video_id=req.video_id,
            artist=req.artist,
            album=req.album,
            title=req.title,
        )
        _jobs[job_id].update({"status": "done", "result": result, "finished_at": time.time()})
    except Exception as e:
        _jobs[job_id].update({"status": "error", "error": str(e), "finished_at": time.time()})


@router.post("")
def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "video_id": req.video_id,
        "title": req.title,
        "artist": req.artist,
        "album": req.album,
        "created_at": time.time(),
    }
    background_tasks.add_task(_run_download, job_id, req)
    return {"job_id": job_id, **_jobs[job_id]}


@router.get("")
def list_downloads():
    return {"jobs": list(_jobs.values())}


@router.get("/{job_id}")
def get_download(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def delete_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    del _jobs[job_id]
    return {"deleted": job_id}