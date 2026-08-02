import pytest

from app.youtube_video import normalize_youtube_url


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
