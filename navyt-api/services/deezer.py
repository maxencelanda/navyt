import re
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEEZER_API = "https://api.deezer.com"


def _clean_title(title: str) -> tuple[str, Optional[str]]:
    """Extract clean title and artist from typical YouTube video titles."""
    noise = re.compile(
        r'[\(\[](official\s*(video|audio|music\s*video|lyric\s*video|visualizer)?'
        r'|lyrics?|hd|hq|4k|remaster(ed)?|explicit|feat\.?.*?|prod\.?.*?'
        r'|official|video|audio|mv|full\s*(album|version)?'
        r'|\d{4})[\)\]]',
        re.IGNORECASE
    )
    cleaned = noise.sub("", title).strip(" -|·•")

    artist = None
    for sep in [" - ", " | ", " – ", " — "]:
        if sep in cleaned:
            parts = cleaned.split(sep, 1)
            artist = parts[0].strip()
            cleaned = parts[1].strip()
            break

    return cleaned, artist


def search_track(title: str, artist: Optional[str] = None) -> Optional[dict]:
    """Search Deezer for a track, return enriched metadata."""
    try:
        clean_title, extracted_artist = _clean_title(title)
        resolved_artist = artist or extracted_artist

        query = f'track:"{clean_title}"'
        if resolved_artist:
            query += f' artist:"{resolved_artist}"'

        resp = requests.get(
            f"{DEEZER_API}/search",
            params={"q": query, "limit": 5},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()

        tracks = data.get("data", [])
        if not tracks:
            # Fallback: looser search without quotes
            fallback_q = f"{clean_title} {resolved_artist or ''}".strip()
            resp = requests.get(
                f"{DEEZER_API}/search",
                params={"q": fallback_q, "limit": 5},
                timeout=8,
            )
            resp.raise_for_status()
            tracks = resp.json().get("data", [])

        if not tracks:
            return None

        track = tracks[0]
        album = track.get("album", {})
        artist_data = track.get("artist", {})

        # Fetch full album for year and genre
        album_id = album.get("id")
        year = None
        genre = None
        if album_id:
            try:
                album_resp = requests.get(
                    f"{DEEZER_API}/album/{album_id}", timeout=8
                )
                album_resp.raise_for_status()
                album_data = album_resp.json()
                release_date = album_data.get("release_date", "")
                year = release_date[:4] if release_date else None
                genres = album_data.get("genres", {}).get("data", [])
                genre = genres[0]["name"] if genres else None
            except Exception as e:
                logger.warning(f"Deezer album fetch failed: {e}")

        return {
            "title": track.get("title"),
            "artist": artist_data.get("name"),
            "album": album.get("title"),
            "year": year,
            "genre": genre,
            "cover_url": album.get("cover_xl") or album.get("cover_big") or album.get("cover"),
            "deezer_id": track.get("id"),
        }

    except Exception as e:
        logger.warning(f"Deezer search failed: {e}")
        return None


def fetch_cover_art(cover_url: str) -> Optional[bytes]:
    """Download cover art from a Deezer cover URL."""
    try:
        resp = requests.get(cover_url, timeout=10)
        if resp.status_code == 200 and resp.content:
            return resp.content
    except Exception as e:
        logger.warning(f"Cover art fetch failed: {e}")
    return None


def embed_tags(
    filepath: str,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    year: Optional[str] = None,
    genre: Optional[str] = None,
    cover_art: Optional[bytes] = None,
) -> None:
    """Embed ID3 tags + cover art into an mp3 file using mutagen."""
    from mutagen.id3 import (
        ID3, ID3NoHeaderError,
        TIT2, TPE1, TALB, TDRC, TCON, APIC
    )
    try:
        try:
            tags = ID3(filepath)
        except ID3NoHeaderError:
            tags = ID3()

        if title:
            tags["TIT2"] = TIT2(encoding=3, text=title)
        if artist:
            tags["TPE1"] = TPE1(encoding=3, text=artist)
        if album:
            tags["TALB"] = TALB(encoding=3, text=album)
        if year:
            tags["TDRC"] = TDRC(encoding=3, text=year)
        if genre:
            tags["TCON"] = TCON(encoding=3, text=genre)
        if cover_art:
            tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=cover_art,
            )

        tags.save(filepath)
        logger.info(f"Tags embedded into {filepath}")

    except Exception as e:
        logger.warning(f"Tag embedding failed: {e}")