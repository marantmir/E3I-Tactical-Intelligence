"""Safe YouTube ingestion for the local computer-vision pipeline."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import logging
import uuid


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
logger = logging.getLogger(__name__)


class _VideoFormatError(ValueError):
    """A public video was inspected, but none of its formats is usable."""


def _format_size(video_format: dict) -> int | None:
    """Return yt-dlp's best size estimate without pretending it is exact."""
    value = video_format.get("filesize") or video_format.get("filesize_approx")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _select_progressive_format(info: dict, max_bytes: int) -> str:
    """Choose a video+audio stream that fits the cap and needs no ffmpeg.

    The production image intentionally does not ship ffmpeg.  Asking yt-dlp for
    ``bestvideo+bestaudio`` therefore made otherwise public videos fail during
    the merge.  YouTube's progressive formats already contain both tracks and
    can be consumed directly by OpenCV.
    """
    progressive = [
        item
        for item in info.get("formats") or []
        if item.get("format_id")
        and item.get("vcodec") not in (None, "none")
        and item.get("acodec") not in (None, "none")
        and (item.get("height") or 0) <= 1080
    ]
    fitting = [item for item in progressive if (_format_size(item) or 0) <= max_bytes]
    if not fitting:
        raise _VideoFormatError(
            "O vídeo não oferece uma versão com áudio e imagem abaixo de 300MB. "
            "Use um vídeo público mais curto ou envie um recorte do arquivo."
        )

    # Prefer a known-size MP4, then the best resolution/bitrate available.  An
    # unknown estimate remains protected by yt-dlp's max_filesize and our final
    # filesystem check.
    fitting.sort(
        key=lambda item: (
            _format_size(item) is not None,
            item.get("ext") == "mp4",
            item.get("height") or 0,
            item.get("tbr") or 0,
        ),
        reverse=True,
    )
    return str(fitting[0]["format_id"])


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
        "outtmpl": output_template,
        "noplaylist": True,
        "max_filesize": max_bytes,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            preview = downloader.extract_info(normalized, download=False)
            downloader.params["format"] = _select_progressive_format(preview, max_bytes)
            info = downloader.extract_info(normalized, download=True)
            prepared = Path(downloader.prepare_filename(info))
    except _VideoFormatError:
        raise
    except Exception as error:
        logger.warning("YouTube download failed for %s: %s", normalized, error)
        raise ValueError(
            "O YouTube recusou o download. Confirme se o vídeo é público, não exige login, "
            "não tem restrição de idade/região e tente novamente."
        ) from error

    candidates = [prepared, prepared.with_suffix(".mp4")]
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
