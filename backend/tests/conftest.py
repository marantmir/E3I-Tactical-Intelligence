import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app import database as database_module


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    """Point the sqlite history/profile store at a throwaway file per test."""
    monkeypatch.setattr(database_module, "DB_PATH", tmp_path / "e3i_tactical_test.db")
    database_module.init_db()
    yield


@pytest.fixture(autouse=True)
def no_network_llm(monkeypatch):
    """Never hit OpenAI/DuckDuckGo from tests; keep the deterministic fallback path."""
    from app import llm_assistant

    monkeypatch.setattr(llm_assistant, "_api_key", lambda: "")


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Rate limiters are process-wide singletons; keep tests independent."""
    from app.rate_limit import video_upload_rate_limiter

    video_upload_rate_limiter.reset()
    yield
    video_upload_rate_limiter.reset()
