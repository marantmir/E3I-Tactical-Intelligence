import json

import pytest

from app.intelligence.config import IntelligenceConfig
from app.intelligence.orchestrator import ToolOrchestrator
from app.intelligence.prompts import FEW_SHOT_CASES, build_grounded_prompt, repair_json_object
from app.intelligence.registry import ToolDefinition, ToolRegistry
from app.intelligence.tools import build_default_registry


def test_default_registry_exposes_four_injected_tools():
    handler = lambda context: {"team": context["team"]}
    registry = build_default_registry(search=handler, ocr=handler, video=handler, metrics=handler)

    assert [item["name"] for item in registry.catalog()] == ["metrics", "ocr", "search", "video"]
    assert registry.get("search").requires_online is True


def test_registry_rejects_duplicates_and_unknown_tools():
    registry = ToolRegistry()
    registry.register(ToolDefinition("video", lambda _: {}))

    with pytest.raises(ValueError, match="already registered"):
        registry.register(ToolDefinition("video", lambda _: {}))
    with pytest.raises(KeyError, match="unknown tool"):
        registry.get("missing")


def test_offline_suite_skips_online_tool_and_annotates_missing_data():
    online_was_called = False

    def search(_):
        nonlocal online_was_called
        online_was_called = True
        return {}

    registry = ToolRegistry()
    registry.register(ToolDefinition("search", search, requires_online=True))
    registry.register(ToolDefinition("metrics", lambda _: {"density": 0.4}))
    result = ToolOrchestrator(registry, IntelligenceConfig(mode="offline")).run(
        ["search", "metrics"], {"team": "E3I FC"}
    )

    assert online_was_called is False
    assert result.outputs == {"metrics": {"density": 0.4}}
    assert result.missing_data[0]["annotation"] == "DADO_AUSENTE"
    assert result.traces[0]["status"] == "skipped"
    assert all("latency_ms" in trace for trace in result.traces)


def test_online_suite_is_fail_soft_and_tracks_latency():
    registry = ToolRegistry()
    registry.register(ToolDefinition("search", lambda _: {"sources": ["mock://source"]}, True))
    registry.register(ToolDefinition("ocr", lambda _: (_ for _ in ()).throw(RuntimeError("mock OCR outage"))))
    result = ToolOrchestrator(registry, IntelligenceConfig(mode="online")).run(["search", "ocr"], {})

    assert result.outputs["search"]["sources"] == ["mock://source"]
    assert result.traces[1]["status"] == "error"
    assert result.missing_data[0]["tool"] == "ocr"
    assert result.total_latency_ms >= 0


def test_grounded_prompt_has_exactly_three_cases_and_missing_data_contract():
    prompt = build_grounded_prompt({"events": []})

    assert len(FEW_SHOT_CASES) == 3
    assert "TOOL_EVIDENCE" in prompt
    assert '"status": "missing"' in prompt


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('```json\n{"ok": true}\n```', {"ok": True}),
        ('preface {"value": 4} trailing text', {"value": 4}),
        ('\ufeff{"items": []}', {"items": []}),
    ],
)
def test_json_repair_handles_transport_noise(raw, expected):
    assert repair_json_object(raw) == expected


def test_json_repair_rejects_invalid_or_non_object_payloads():
    with pytest.raises(ValueError):
        repair_json_object("not json")
    with pytest.raises(ValueError, match="JSON object"):
        repair_json_object(json.dumps([1, 2]))


def test_config_reads_and_clamps_environment(monkeypatch):
    monkeypatch.setenv("E3I_INTELLIGENCE_MODE", "online")
    monkeypatch.setenv("E3I_MAX_PARALLEL_TOOLS", "99")
    monkeypatch.setenv("E3I_TOOL_TIMEOUT_SECONDS", "bad")
    config = IntelligenceConfig.from_env()

    assert config.mode == "online"
    assert config.max_parallel_tools == 16
    assert config.tool_timeout_seconds == 12.0
