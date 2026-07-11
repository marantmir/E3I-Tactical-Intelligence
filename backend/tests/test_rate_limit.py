import time

import pytest

from app.rate_limit import RateLimiter, video_upload_rate_limiter


def test_rate_limiter_allows_requests_within_the_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60)

    for _ in range(3):
        limiter.check("client-a")


def test_rate_limiter_blocks_once_limit_is_exceeded():
    limiter = RateLimiter(max_requests=2, window_seconds=60)

    limiter.check("client-b")
    limiter.check("client-b")

    with pytest.raises(Exception) as exc_info:
        limiter.check("client-b")

    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers


def test_rate_limiter_tracks_clients_independently():
    limiter = RateLimiter(max_requests=1, window_seconds=60)

    limiter.check("client-c")
    limiter.check("client-d")  # different key, should not be blocked


def test_rate_limiter_resets_after_window_elapses():
    limiter = RateLimiter(max_requests=1, window_seconds=0.05)

    limiter.check("client-e")
    time.sleep(0.07)
    limiter.check("client-e")  # window elapsed, should be allowed again


def test_reset_clears_all_tracked_clients():
    limiter = RateLimiter(max_requests=1, window_seconds=60)

    limiter.check("client-f")
    limiter.reset()
    limiter.check("client-f")  # allowed again after reset


def test_video_upload_rate_limiter_is_shared_singleton():
    assert video_upload_rate_limiter.max_requests > 0
    assert video_upload_rate_limiter.window_seconds > 0
