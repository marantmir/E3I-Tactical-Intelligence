from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from app.youtube_video import download_youtube_video, normalize_youtube_url


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123?t=10",
        "https://youtube.com/shorts/abc123",
    ],
)
def test_normalize_youtube_url_accepts_supported_video_links(url: str):
    assert normalize_youtube_url(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://youtube.com/watch?v=abc123",
        "https://example.com/watch?v=abc123",
        "https://youtube.com/results?search_query=futebol",
        "file:///etc/passwd",
    ],
)
def test_normalize_youtube_url_rejects_unsafe_or_non_video_links(url: str):
    with pytest.raises(ValueError):
        normalize_youtube_url(url)


def _install_fake_ytdlp(monkeypatch, tmp_path: Path, formats: list[dict]):
    calls = []

    class FakeDownloader:
        def __init__(self, options):
            self.params = dict(options)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def extract_info(self, _url, download):
            calls.append((download, self.params.get("format")))
            info = {"id": "public123", "title": "Treino público", "formats": formats, "duration": 42}
            if download:
                Path(self.prepare_filename(info)).write_bytes(b"video")
            return info

        def prepare_filename(self, _info):
            return str(tmp_path / "download.mp4")

    monkeypatch.setitem(sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=FakeDownloader))
    return calls


def test_download_uses_progressive_stream_under_limit_without_ffmpeg(monkeypatch, tmp_path):
    calls = _install_fake_ytdlp(
        monkeypatch,
        tmp_path,
        [
            {"format_id": "video-only", "vcodec": "avc1", "acodec": "none", "height": 1080},
            {
                "format_id": "progressive-360",
                "vcodec": "avc1",
                "acodec": "mp4a",
                "height": 360,
                "ext": "mp4",
                "filesize": 10_000,
            },
            {
                "format_id": "progressive-too-large",
                "vcodec": "avc1",
                "acodec": "mp4a",
                "height": 720,
                "ext": "mp4",
                "filesize": 400_000_000,
            },
        ],
    )

    path, source = download_youtube_video(
        "https://www.youtube.com/watch?v=public123", tmp_path, 300 * 1024 * 1024
    )

    assert path == tmp_path / "download.mp4"
    assert source["video_id"] == "public123"
    assert calls == [(False, None), (True, "progressive-360")]


def test_download_rejects_video_without_progressive_stream_below_limit(monkeypatch, tmp_path):
    calls = _install_fake_ytdlp(
        monkeypatch,
        tmp_path,
        [
            {
                "format_id": "large",
                "vcodec": "avc1",
                "acodec": "mp4a",
                "height": 720,
                "filesize_approx": 400_000_000,
            }
        ],
    )

    with pytest.raises(ValueError, match="não oferece uma versão"):
        download_youtube_video("https://youtu.be/public123", tmp_path, 300 * 1024 * 1024)

    assert calls == [(False, None)]
