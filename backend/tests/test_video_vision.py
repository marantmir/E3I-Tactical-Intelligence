from pathlib import Path

import cv2
import numpy as np
import pytest

from app.video_vision import process_video


def _write_synthetic_match_clip(path: Path, frames: int = 60, fps: float = 25.0, size: tuple[int, int] = (320, 240)) -> None:
    """Builds a short synthetic clip: green pitch background with two moving
    dark blobs, so the MOG2 + contour pipeline has real motion to track."""
    width, height = size
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    assert writer.isOpened()

    for frame_idx in range(frames):
        frame = np.full((height, width, 3), (60, 160, 60), dtype=np.uint8)

        x1 = 20 + int((width - 60) * (frame_idx / frames))
        y1 = 60
        cv2.rectangle(frame, (x1, y1), (x1 + 18, y1 + 40), (20, 20, 200), -1)

        x2 = width - 30 - int((width - 60) * (frame_idx / frames))
        y2 = 140
        cv2.rectangle(frame, (x2, y2), (x2 + 18, y2 + 40), (200, 20, 20), -1)

        writer.write(frame)

    writer.release()


@pytest.fixture
def synthetic_video(tmp_path: Path) -> Path:
    video_path = tmp_path / "synthetic_match.mp4"
    _write_synthetic_match_clip(video_path)
    return video_path


def test_process_video_returns_expected_shape(synthetic_video: Path):
    result = process_video(str(synthetic_video), max_frames=60, sample_every=1, team_filter="all")

    assert result["status"] == "processed"
    assert result["frames_analyzed"] > 0
    assert "movement_tracks" in result
    assert "heatmap" in result
    assert "graph" in result
    assert set(result["graph"].keys()) == {"nodes", "edges", "metrics"}


def test_process_video_detects_moving_tracks(synthetic_video: Path):
    result = process_video(str(synthetic_video), max_frames=60, sample_every=1, team_filter="all")

    assert result["tracks_detected"] >= 1
    for track in result["movement_tracks"]:
        assert track["distance_px"] >= 0
        assert "team_label" in track


def test_process_video_respects_max_frames(synthetic_video: Path):
    result = process_video(str(synthetic_video), max_frames=10, sample_every=1, team_filter="all")

    assert result["frames_analyzed"] <= 10


def test_process_video_rejects_unreadable_file(tmp_path: Path):
    bogus_path = tmp_path / "not_a_video.mp4"
    bogus_path.write_bytes(b"this is not a real video file")

    with pytest.raises(ValueError):
        process_video(str(bogus_path))
