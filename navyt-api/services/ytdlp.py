import yt_dlp
import os
from typing import Optional

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

    artist_safe = _sanitize(artist or "Unknown Artist")
    album_safe = _sanitize(album or "Unknown Album")
    out_dir = os.path.join(MEDIA_DIR, artist_safe, album_safe)
    os.makedirs(out_dir, exist_ok=True)

    outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")
    if title:
        outtmpl = os.path.join(out_dir, f"{_sanitize(title)}.%(ext)s")

    opts = _base_opts({
        "format": "140/251/250/249/139/18",
        "outtmpl": outtmpl,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
        "postprocessor_args": {
            "ffmpeg": [
                *(
                    [
                        "-metadata", f"artist={artist}",
                        "-metadata", f"album={album}",
                        "-metadata", f"title={title}",
                    ]
                    if any([artist, album, title]) else []
                ),
            ]
        },
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return {
            "video_id": video_id,
            "title": title or info.get("title"),
            "artist": artist,
            "album": album,
            "output_dir": out_dir,
        }


def _sanitize(name: str) -> str:
    """Remove filesystem-unsafe characters."""
    keep = set(" .-_()[]")
    return "".join(c if c.isalnum() or c in keep else "_" for c in name).strip()