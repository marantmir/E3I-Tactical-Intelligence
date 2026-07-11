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


def test_process_video_samples_the_full_duration_of_long_clips(tmp_path: Path):
    """A video much longer than max_frames must still be analyzed end to end
    (samples spread across the whole clip), not just its first few seconds."""
    video_path = tmp_path / "long_synthetic_match.mp4"
    _write_synthetic_match_clip(video_path, frames=300, fps=25.0)

    result = process_video(str(video_path), max_frames=10, sample_every=1, team_filter="all")

    config = result["processing_config"]
    assert config["full_video_coverage"] is True
    assert config["source_total_frames"] == 300
    assert config["requested_sample_every"] == 1
    # 300 source frames spread across only 10 samples means each sample must be
    # ~30 frames apart - i.e. the last sample lands near the end of the clip,
    # not clustered in the first 10 frames like the old sequential behavior.
    assert config["sample_every"] >= 30
    assert result["frames_analyzed"] <= 10


_REAL_VIDEO_CAPTURE = cv2.VideoCapture


class _FakeCaptureBase:
    """Wraps a real cv2.VideoCapture by composition (not subclassing - the
    OpenCV binding is a C extension type, and subclassing/overriding it in
    Python has caused segfaults when combined with `super()` calls)."""

    def __init__(self, path):
        self._real = _REAL_VIDEO_CAPTURE(path)

    def isOpened(self):
        return self._real.isOpened()

    def get(self, prop_id):
        return self._real.get(prop_id)

    def set(self, prop_id, value):
        return self._real.set(prop_id, value)

    def read(self):
        return self._real.read()

    def release(self):
        return self._real.release()


def test_process_video_recovers_full_coverage_when_metadata_reports_zero_frames(tmp_path: Path, monkeypatch):
    """Some codecs/containers (phone recordings, unfinalized webm) report
    CAP_PROP_FRAME_COUNT as 0/unreliable even though the file is fully
    seekable. Probing must recover the real length directly instead of
    silently falling back to analyzing only the first few frames."""
    video_path = tmp_path / "long_synthetic_match.mp4"
    _write_synthetic_match_clip(video_path, frames=300, fps=25.0)

    class _UnreliableMetadataCapture(_FakeCaptureBase):
        def get(self, prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT:
                return 0
            return super().get(prop_id)

    monkeypatch.setattr("app.video_vision.cv2.VideoCapture", _UnreliableMetadataCapture)

    result = process_video(str(video_path), max_frames=10, sample_every=1, team_filter="all")

    config = result["processing_config"]
    assert config["full_video_coverage"] is True
    assert config["source_total_frames"] == 300
    assert config["sample_every"] >= 30


def test_process_video_recovers_full_coverage_when_metadata_underestimates(tmp_path: Path, monkeypatch):
    """Some containers report a frame count lower than the real content
    (e.g. truncated index). Probing must detect and correct for this too."""
    video_path = tmp_path / "long_synthetic_match.mp4"
    _write_synthetic_match_clip(video_path, frames=300, fps=25.0)

    class _UnderestimatingCapture(_FakeCaptureBase):
        def get(self, prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT:
                return 50  # real file has 300 frames
            return super().get(prop_id)

    monkeypatch.setattr("app.video_vision.cv2.VideoCapture", _UnderestimatingCapture)

    result = process_video(str(video_path), max_frames=10, sample_every=1, team_filter="all")

    config = result["processing_config"]
    assert config["full_video_coverage"] is True
    assert config["source_total_frames"] == 300


def test_process_video_falls_back_to_sequential_when_seeking_is_unsupported(tmp_path: Path, monkeypatch):
    """If the capture cannot seek at all (rare, e.g. some live/network
    streams), keep the old sequential-from-start behavior instead of
    crashing or looping forever trying to probe the length."""
    video_path = tmp_path / "synthetic_match.mp4"
    _write_synthetic_match_clip(video_path, frames=60, fps=25.0)

    class _NoSeekCapture(_FakeCaptureBase):
        def set(self, prop_id, value):
            if prop_id == cv2.CAP_PROP_POS_FRAMES:
                return False
            return super().set(prop_id, value)

    monkeypatch.setattr("app.video_vision.cv2.VideoCapture", _NoSeekCapture)

    result = process_video(str(video_path), max_frames=10, sample_every=2, team_filter="all")

    config = result["processing_config"]
    assert config["full_video_coverage"] is False
    assert config["source_total_frames"] == 0
    assert config["sample_every"] == 2


def test_process_video_rejects_unreadable_file(tmp_path: Path):
    bogus_path = tmp_path / "not_a_video.mp4"
    bogus_path.write_bytes(b"this is not a real video file")

    with pytest.raises(ValueError):
        process_video(str(bogus_path))
