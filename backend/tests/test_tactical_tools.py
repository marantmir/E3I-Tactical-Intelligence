import json
import time

import pytest

from app.llm_tool_orchestrator import LLMToolOrchestrator, NormalizedModelResponse, NormalizedToolCall
from app.tool_registry import (
    ToolDefinition, ToolExecutionError, ToolRegistry, ToolSizeLimitError,
    ToolTimeoutError, ToolValidationError, create_default_tool_registry,
)


TOOLS = {
    "search_tactical_information": {"team_name": "Time A", "query": "pressao", "max_sources": 3},
    "extract_tactical_ocr": {"team_name": "Time A", "vision_result": {"visual_key_frames": {"frames": []}}},
    "analyze_video_frames": {"team_name": "Time A", "vision_result": {"summary": "amostra"}},
    "calculate_tactical_metrics": {"team_id": 1},
    "run_operational_research": {"team_id": 1, "formation": "4-3-3"},
    "get_team_context": {"team_id": 1},
}


@pytest.mark.parametrize(("name", "valid"), TOOLS.items())
def test_each_tactical_tool_schema_rejects_missing_extra_wrong_type_and_oversize(name, valid):
    registry = create_default_tool_registry()
    required = next(iter(valid))
    missing = {key: value for key, value in valid.items() if key != required}
    with pytest.raises(ToolValidationError):
        registry.execute(name, missing)
    with pytest.raises(ToolValidationError):
        registry.execute(name, {**valid, "private_config": "no"})
    with pytest.raises(ToolValidationError):
        registry.execute(name, {**valid, required: 1.5})
    definition = registry.get(name)
    bounded = ToolRegistry()
    bounded.register(ToolDefinition(name, "bounded", definition.input_model, definition.execute, max_input_bytes=10))
    with pytest.raises(ToolSizeLimitError):
        bounded.execute(name, valid)


def test_tactical_wrappers_delegate_and_normalize_outputs(monkeypatch):
    monkeypatch.setattr("app.tactical_tools.search_tactical_enhanced", lambda *a, **k: {"sources": [{"title": "A"}]})
    monkeypatch.setattr("app.tactical_tools.analyze_video_visually", lambda *a: {"text": "placar incerto"})
    monkeypatch.setattr("app.tactical_tools.analyze_video_tactics", lambda *a: {"patterns": []})
    registry = create_default_tool_registry()

    for name in ("search_tactical_information", "extract_tactical_ocr", "analyze_video_frames",
                 "calculate_tactical_metrics", "run_operational_research", "get_team_context"):
        output = registry.execute(name, TOOLS[name])
        assert set(output) == {"provenance", "data", "limitations"}
        assert output["provenance"]["service"]
        assert output["provenance"]["nature"] in {"real", "heuristic", "external_unavailable"}
        json.dumps(output)


@pytest.mark.parametrize("name", TOOLS)
def test_each_tactical_tool_timeout_and_service_failure_are_sanitized(name):
    source = create_default_tool_registry().get(name)
    timeout_registry = ToolRegistry()
    timeout_registry.register(ToolDefinition(name, "slow", source.input_model, lambda _: time.sleep(.03), timeout_seconds=.001))
    with pytest.raises(ToolTimeoutError, match="timed out"):
        timeout_registry.execute(name, TOOLS[name])

    failure_registry = ToolRegistry()
    def fail(_):
        raise RuntimeError("token=secret internal=/srv/private")
    failure_registry.register(ToolDefinition(name, "fail", source.input_model, fail))
    with pytest.raises(ToolExecutionError, match="Tool execution failed") as error:
        failure_registry.execute(name, TOOLS[name])
    assert "secret" not in str(error.value)
    assert "/srv" not in str(error.value)


class TacticalAdapter:
    provider = "mock"
    def __init__(self):
        self.calls = 0
        self.requests = []
    def complete(self, messages, tools):
        self.requests.append(messages)
        self.calls += 1
        if self.calls == 1:
            return NormalizedModelResponse(tool_calls=(NormalizedToolCall("ctx", "get_team_context", {"team_id": 1}),))
        if self.calls == 2:
            assert messages[-1]["name"] == "get_team_context"
            assert messages[-1]["content"]["data"]["team"]["id"] == 1
            return NormalizedModelResponse(tool_calls=(NormalizedToolCall("metrics", "calculate_tactical_metrics", {"team_id": 1}),))
        return NormalizedModelResponse(content="Contexto e metricas considerados.")


def test_orchestrator_calls_two_tactical_tools_preserves_context_and_finishes():
    adapter = TacticalAdapter()
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("Analise o time 1")
    assert result.content == "Contexto e metricas considerados."
    assert [message["tool_call_id"] for message in result.history if message["role"] == "tool"] == ["ctx", "metrics"]
