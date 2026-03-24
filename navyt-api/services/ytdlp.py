import yt_dlp
import os
from typing import Optional
import glob
import logging
from services.deezer import search_track, fetch_cover_art, embed_tags

logger = logging.getLogger(__name__)

MEDIA_DIR = os.getenv("NAVIDROME_MEDIA_DIR", "/music")


def _base_opts(extra: dict = {}) -> dict:
    return {
        "quiet": True,
        "no_warnings": True,
        **extra,
    }


def search_videos(query: str, max_results: int = 20) -> list[dict]:
    opts = _base_opts({
        "extract_flat": "in_playlist",
        "default_search": f"ytsearch{max_results}",
    })
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(query, download=False)
        entries = result.get("entries", [])
        return [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "channel": e.get("channel") or e.get("uploader"),
                "duration": e.get("duration"),
                "thumbnail": e.get("thumbnail")
                    or f"https://i.ytimg.com/vi/{e.get('id')}/hqdefault.jpg",
                "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                "view_count": e.get("view_count"),
            }
            for e in entries
            if e.get("id")
        ]


def get_video_info(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = _base_opts({"extract_flat": False})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "channel": info.get("channel") or info.get("uploader"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "url": url,
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "acodec": f.get("acodec"),
                    "vcodec": f.get("vcodec"),
                    "abr": f.get("abr"),
                    "filesize": f.get("filesize"),
                }
                for f in info.get("formats", [])
                if f.get("acodec") != "none"
            ],
        }


def download_audio(
    video_id: str,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    title: Optional[str] = None,
) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"

    with yt_dlp.YoutubeDL(_base_opts()) as ydl:
        info = ydl.extract_info(url, download=False)
    
    yt_title = info.get("title", video_id)
    yt_channel = info.get("channel") or info.get("uploader")
    
    dz_meta = search_track(title or yt_title, artist or yt_channel)
    logger.info(f"Deezer match for '{yt_title}': {dz_meta}")
    
    final_title  = title  or (dz_meta and dz_meta["title"])  or yt_title
    final_artist = artist or (dz_meta and dz_meta["artist"]) or yt_channel or "Unknown Artist"
    final_album  = album  or (dz_meta and dz_meta["album"])  or "Unknown Album"
    final_year   = dz_meta and dz_meta.get("year")
    final_genre  = dz_meta and dz_meta.get("genre")
    cover_url    = dz_meta and dz_meta.get("cover_url")

    artist_safe = _sanitize(final_artist)
    album_safe  = _sanitize(final_album)
    out_dir = os.path.join(MEDIA_DIR, artist_safe, album_safe)
    os.makedirs(out_dir, exist_ok=True)

    outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")
    if final_title:
        outtmpl = os.path.join(out_dir, f"{_sanitize(final_title)}.%(ext)s")

    opts = _base_opts({
        "format": "251/140/250/249/139/18",
        "outtmpl": outtmpl,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
        ],
    })

    # Step 2 — download
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Step 3 — find the output file
    search_title = _sanitize(final_title or info.get("title", video_id))
    matches = glob.glob(os.path.join(out_dir, f"{search_title}*.mp3"))
    if not matches:
        matches = glob.glob(os.path.join(out_dir, "*.mp3"))
    mp3_path = matches[0] if matches else None

    # Step 4 — embed tags + cover art
    if mp3_path:
        cover_art = fetch_cover_art(cover_url) if cover_url else None

        embed_tags(
            filepath=mp3_path,
            title=final_title or info.get("title"),
            artist=final_artist,
            album=final_album,
            year=final_year,
            genre=final_genre,
            cover_art=cover_art,
        )

    return {
        "video_id": video_id,
        "title": final_title or info.get("title"),
        "artist": final_artist,
        "album": final_album,
        "year": final_year,
        "genre": final_genre,
        "deezer_match": dz_meta is not None,
        "output_path": mp3_path,
        "output_dir": out_dir,
    }


def _sanitize(name: str) -> str:
    """Remove filesystem-unsafe characters."""
    keep = set(" .-_()[]")
    return "".join(c if c.isalnum() or c in keep else "_" for c in name).strip()