from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from services.ytdlp import search_videos, get_video_info
from services.deezer import search_track

router = APIRouter()


@router.get("")
def search(q: str = Query(..., min_length=1), max_results: int = Query(20, ge=1, le=50)):
    try:
        return {"results": search_videos(q, max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deezer")
def deezer_preview(title: str, artist: Optional[str] = None):
    result = search_track(title, artist)
    if result:
        return {"found": True, **result}
    return {"found": False}

@router.get("/{video_id}")
def video_info(video_id: str):
    try:
        return get_video_info(video_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
