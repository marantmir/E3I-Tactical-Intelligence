import io

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.routes import teams as teams_routes


client = TestClient(app)

STUB_ONLINE_SEARCH = {
    "status": "unavailable",
    "query": "time futebol analise tatica videos",
    "summary": "Busca offline nos testes.",
    "sources": [],
    "source_groups": {"match_videos": [], "analysis_videos": [], "team_form": []},
    "coverage": {"match_videos": 0, "analysis_videos": 0, "team_form": 0},
    "analysis_focus": [],
    "collection_plan": [],
    "retrieved_at": "2026-01-01T00:00:00+00:00",
    "errors": [],
    "note": "stub",
}


def _stub_search_public_team_info(_team_name: str) -> dict:
    return STUB_ONLINE_SEARCH


def _mock_online_search(monkeypatch):
    monkeypatch.setattr(teams_routes, "search_public_team_info", _stub_search_public_team_info)


def test_list_teams_returns_seed_data():
    response = client.get("/api/teams")

    assert response.status_code == 200
    teams = response.json()
    assert len(teams) >= 1
    assert {"id", "name", "league"}.issubset(teams[0].keys())


def test_team_detail_found():
    response = client.get("/api/teams/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_team_detail_not_found_returns_404():
    response = client.get("/api/teams/999999")

    assert response.status_code == 404


def test_team_graph_analysis_returns_nodes_and_edges():
    response = client.get("/api/teams/1/graph-analysis")

    assert response.status_code == 200
    payload = response.json()
    assert payload["nodes"]
    assert payload["edges"]


def test_team_related_records_endpoints():
    for suffix in ("formations", "players", "sources", "tactical-analysis", "game-plan"):
        response = client.get(f"/api/teams/1/{suffix}")
        assert response.status_code == 200, suffix


def test_team_public_intelligence_uses_online_search(monkeypatch):
    _mock_online_search(monkeypatch)

    response = client.get("/api/teams/1/public-intelligence")

    assert response.status_code == 200
    assert response.json() == STUB_ONLINE_SEARCH


def _synthetic_video_bytes() -> bytes:
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "clip.mp4"
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 25.0, (160, 120))
        for i in range(20):
            frame = np.full((120, 160, 3), (60, 160, 60), dtype=np.uint8)
            cv2.rectangle(frame, (10 + i * 3, 40), (30 + i * 3, 80), (20, 20, 200), -1)
            writer.write(frame)
        writer.release()
        return path.read_bytes()


def test_video_vision_upload_rejects_unsupported_extension():
    response = client.post(
        "/api/teams/1/video-vision/upload",
        files={"file": ("clip.txt", b"not a video", "text/plain")},
    )

    assert response.status_code == 400


def test_video_vision_upload_processes_synthetic_clip():
    video_bytes = _synthetic_video_bytes()

    response = client.post(
        "/api/teams/1/video-vision/upload",
        params={"max_frames": 60, "sample_every": 1, "team_filter": "all"},
        files={"file": ("clip.mp4", io.BytesIO(video_bytes), "video/mp4")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "processed"
    assert payload["team"] == "Flamengo"
    assert payload["annotated_video_url"].startswith("/media/")
