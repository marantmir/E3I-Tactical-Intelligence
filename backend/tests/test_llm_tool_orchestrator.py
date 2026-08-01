import time
import io
import logging

from pydantic import BaseModel, ConfigDict

from app.llm_tool_orchestrator import (
    LLMToolOrchestrator,
    NormalizedModelResponse,
    NormalizedToolCall,
)
from app.tool_registry import ToolDefinition, ToolRegistry, create_default_tool_registry
from app.logging_config import JsonLogFormatter


class EmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScriptedAdapter:
    provider = "mock_provider"

    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, messages, tools):
        self.requests.append((messages, tools))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def call(call_id="call-1", name="get_llm_status", arguments=None):
    return NormalizedModelResponse(
        tool_calls=(NormalizedToolCall(call_id, name, {} if arguments is None else arguments),)
    )


def test_mock_model_tool_result_same_model_final_response(monkeypatch):
    monkeypatch.setattr("app.tool_registry.llm_status", lambda: {"enabled": False, "has_api_key": False})
    adapter = ScriptedAdapter([call(), NormalizedModelResponse(content="LLM local está desativado.")])

    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("Qual é o status?")

    assert result.content == "LLM local está desativado."
    assert result.used_fallback is False
    assert adapter.requests[0][0][-1] == {"role": "user", "content": "Qual é o status?"}
    returned = adapter.requests[1][0][-1]
    assert returned["role"] == "tool"
    assert returned["tool_call_id"] == "call-1"
    assert returned["content"] == {"enabled": False, "has_api_key": False}
    assert "get_llm_status" in [tool["name"] for tool in adapter.requests[0][1]]


def test_unknown_tool_is_rejected_and_error_returns_to_model():
    adapter = ScriptedAdapter([call(name="run_shell"), NormalizedModelResponse(content="recusada")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("execute")
    tool_message = result.history[-2]
    assert tool_message["status"] == "error"
    assert tool_message["content"] == {"error": "Tool is not available"}


def test_invalid_arguments_are_rejected():
    adapter = ScriptedAdapter([call(arguments={"secret": "no"}), NormalizedModelResponse(content="inválido")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("status")
    assert result.history[-2]["content"] == {"error": "Tool arguments are invalid"}


def test_json_string_arguments_are_normalized_and_validated(monkeypatch):
    monkeypatch.setattr("app.tool_registry.llm_status", lambda: {"enabled": False})
    adapter = ScriptedAdapter([call(arguments="{}"), NormalizedModelResponse(content="ok")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("status")
    assert result.history[-2]["status"] == "success"


def test_tool_timeout_is_safe():
    registry = ToolRegistry()
    registry.register(ToolDefinition("slow", "slow", EmptyInput, lambda _: time.sleep(0.05), timeout_seconds=0.001))
    adapter = ScriptedAdapter([call(name="slow"), NormalizedModelResponse(content="timeout tratado")])
    result = LLMToolOrchestrator(adapter, registry).run("slow")
    assert result.history[-2]["content"] == {"error": "Tool execution timed out"}


def test_two_sequential_calls_and_history_are_preserved(monkeypatch):
    monkeypatch.setattr("app.tool_registry.llm_status", lambda: {"enabled": False})
    prior = [{"role": "system", "content": "safe"}]
    adapter = ScriptedAdapter([call("one"), call("two"), NormalizedModelResponse(content="done")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("status twice", history=prior)
    assert [message["tool_call_id"] for message in result.history if message["role"] == "tool"] == ["one", "two"]
    assert result.history[0] == prior[0]
    assert len(adapter.requests) == 3


def test_iteration_limit_interrupts_infinite_loop_with_fallback():
    adapter = ScriptedAdapter([call(str(index)) for index in range(4)])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry(), fallback=lambda _: "local").run("loop")
    assert result.iterations == 4
    assert result.used_fallback is True
    assert result.content == "local"


def test_iteration_configuration_is_bounded():
    adapter = ScriptedAdapter([])
    for invalid in (0, 9):
        try:
            LLMToolOrchestrator(adapter, create_default_tool_registry(), max_iterations=invalid)
        except ValueError as exc:
            assert "between 1 and 8" in str(exc)
        else:
            raise AssertionError("invalid iteration limit accepted")


def test_large_result_is_rejected():
    registry = ToolRegistry()
    registry.register(ToolDefinition("large", "large", EmptyInput, lambda _: "x" * 100, max_output_bytes=20))
    adapter = ScriptedAdapter([call(name="large"), NormalizedModelResponse(content="too large")])
    result = LLMToolOrchestrator(adapter, registry).run("large")
    assert result.history[-2]["content"] == {"error": "Tool result exceeds the size limit"}


def test_large_arguments_are_rejected_before_execution():
    adapter = ScriptedAdapter([call(arguments={"value": "x" * 30}), NormalizedModelResponse(content="too large")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry(), max_argument_bytes=20).run("large")
    assert result.history[-2]["content"] == {"error": "Tool arguments exceed the size limit"}


def test_internal_tool_error_is_sanitized():
    registry = ToolRegistry()

    def explode(_):
        raise RuntimeError("password=super-secret")

    registry.register(ToolDefinition("explode", "explode", EmptyInput, explode))
    adapter = ScriptedAdapter([call(name="explode"), NormalizedModelResponse(content="safe")])
    result = LLMToolOrchestrator(adapter, registry).run("explode")
    assert result.history[-2]["content"] == {"error": "Tool execution failed"}
    assert "super-secret" not in str(result.history)


def test_absent_credentials_do_not_break_status_flow(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("app.llm_assistant._api_key", lambda: "")
    adapter = ScriptedAdapter([call(), NormalizedModelResponse(content="sem credencial")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry()).run("status")
    assert result.content == "sem credencial"
    assert result.history[-2]["content"]["has_api_key"] is False


def test_model_failure_uses_deterministic_fallback():
    adapter = ScriptedAdapter([RuntimeError("provider leaked a token")])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry(), fallback=lambda prompt: f"local:{prompt}").run("oi")
    assert result.content == "local:oi"
    assert result.used_fallback is True
    assert "provider leaked" not in str(result.history)


def test_empty_model_response_uses_fallback():
    adapter = ScriptedAdapter([NormalizedModelResponse()])
    result = LLMToolOrchestrator(adapter, create_default_tool_registry(), fallback=lambda _: "local").run("oi")
    assert result.content == "local"
    assert result.used_fallback is True


def test_logs_metadata_without_argument_contents():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonLogFormatter())
    logger = logging.getLogger("e3i")
    old_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    adapter = ScriptedAdapter([call(arguments={"secret": "do-not-log"}), NormalizedModelResponse(content="done")])
    try:
        LLMToolOrchestrator(adapter, create_default_tool_registry()).run("status")
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)
    output = stream.getvalue()
    assert "llm_tool_orchestration" in output
    assert "mock_provider" in output
    assert "get_llm_status" in output
    assert "do-not-log" not in output
