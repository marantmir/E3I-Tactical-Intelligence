"""Safe YouTube ingestion for the local computer-vision pipeline."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import uuid


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def normalize_youtube_url(value: str) -> str:
    """Validate that *value* is an HTTPS YouTube video URL.

    Keeping the allow-list here prevents the downloader endpoint from becoming
    a generic server-side URL fetcher.
    """
    url = (value or "").strip()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in YOUTUBE_HOSTS:
        raise ValueError("Informe um link HTTPS válido do YouTube.")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    else:
        from urllib.parse import parse_qs

        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id and parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/")[2]
    if not video_id:
        raise ValueError("O link precisa apontar para um vídeo do YouTube.")
    return url


def download_youtube_video(url: str, destination: Path, max_bytes: int) -> tuple[Path, dict]:
    """Download one public video with yt-dlp, enforcing the upload size cap."""
    normalized = normalize_youtube_url(url)
    try:
        import yt_dlp
    except ImportError as error:  # pragma: no cover - deployment packaging guard
        raise RuntimeError("O suporte a links do YouTube não está instalado no servidor.") from error

    destination.mkdir(parents=True, exist_ok=True)
    output_template = str(destination / f"youtube_{uuid.uuid4().hex}.%(ext)s")
    options = {
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "max_filesize": max_bytes,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(normalized, download=True)
            prepared = Path(downloader.prepare_filename(info))
    except Exception as error:
        raise ValueError(
            "Não foi possível baixar o vídeo. Confirme se ele é público, não exige login e tem até 300MB."
        ) from error

    candidates = [prepared.with_suffix(".mp4"), prepared]
    video_path = next((path for path in candidates if path.exists()), None)
    if video_path is None:
        raise ValueError("O YouTube não forneceu um arquivo de vídeo compatível.")
    if video_path.stat().st_size > max_bytes:
        video_path.unlink(missing_ok=True)
        raise ValueError("Vídeo do YouTube excede o limite de 300MB.")
    return video_path, {
        "type": "youtube",
        "url": normalized,
        "title": info.get("title") or "Vídeo do YouTube",
        "video_id": info.get("id"),
        "duration_seconds": info.get("duration"),
    }
