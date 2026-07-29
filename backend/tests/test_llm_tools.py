import time

import pytest
from pydantic import BaseModel, ConfigDict

from app.llm_orchestration import ProviderTurn, ToolCall, run_tool_loop
from app.llm_tools import ToolError, ToolRegistry


class LookupArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str


def registry_with_lookup(handler=lambda query: {"query": query}):
    registry = ToolRegistry()
    registry.register("lookup", "Busca local", LookupArguments, handler)
    return registry


def test_tool_registration_exposes_provider_schema():
    definition = registry_with_lookup().definitions()[0]
    assert definition["name"] == "lookup"
    assert definition["parameters"]["required"] == ["query"]


@pytest.mark.parametrize(
    ("name", "arguments", "message"),
    [
        ("missing", {"query": "x"}, "tool not found"),
        ("lookup", {}, "invalid tool arguments: query"),
        ("lookup", {"query": "x", "secret": True}, "invalid tool arguments: secret"),
        ("lookup", "not-an-object", "invalid tool arguments"),
    ],
)
def test_invalid_tool_calls_are_safe(name, arguments, message):
    with pytest.raises(ToolError, match=message):
        registry_with_lookup().execute(name, arguments)


def test_valid_arguments_are_passed_to_tool():
    assert registry_with_lookup().execute("lookup", {"query": "pressão"}) == '{"query":"pressão"}'


def test_timeout_does_not_wait_for_slow_tool():
    def slow(query):
        time.sleep(0.2)

    started = time.monotonic()
    with pytest.raises(ToolError, match="timed out"):
        registry_with_lookup(slow).execute("lookup", {"query": "x"}, timeout_seconds=0.01)
    assert time.monotonic() - started < 0.15


def test_internal_error_is_sanitized():
    def broken(query):
        raise RuntimeError("token=super-secret")

    with pytest.raises(ToolError) as raised:
        registry_with_lookup(broken).execute("lookup", {"query": "x"})
    assert str(raised.value) == "tool execution failed"
    assert "secret" not in str(raised.value)


@pytest.mark.parametrize("empty", [None, "", [], {}])
def test_empty_results_are_normalized(empty):
    assert registry_with_lookup(lambda query: empty).execute("lookup", {"query": "x"}) == "No result available."


class ScriptedProvider:
    def __init__(self, *turns):
        self.turns = list(turns)
        self.contexts = []

    def complete(self, messages, tools):
        self.contexts.append([dict(message) for message in messages])
        turn = self.turns.pop(0)
        if isinstance(turn, Exception):
            raise turn
        return turn


def test_response_without_tool_completes_directly():
    result = run_tool_loop(ScriptedProvider(ProviderTurn(text="resposta")), registry_with_lookup(), [{"role": "user", "content": "oi"}])
    assert (result.text, result.status, result.iterations) == ("resposta", "completed", 0)


def test_large_tool_response_is_bounded():
    provider = ScriptedProvider(
        ProviderTurn(tool_calls=(ToolCall("1", "lookup", {"query": "x"}),)),
        ProviderTurn(text="ok"),
    )
    result = run_tool_loop(provider, registry_with_lookup(lambda query: "x" * 100), [{"role": "user", "content": "u"}], maximum_tool_result_chars=10)
    assert result.status == "completed"
    assert provider.contexts[1][-1]["content"] == "xxxxxxxxxx…[truncated]"


def test_two_sequential_tools_preserve_context():
    provider = ScriptedProvider(
        ProviderTurn(tool_calls=(ToolCall("1", "lookup", {"query": "primeira"}),)),
        ProviderTurn(tool_calls=(ToolCall("2", "lookup", {"query": "segunda"}),)),
        ProviderTurn(text="síntese"),
    )
    original = [{"role": "system", "content": "regras"}, {"role": "user", "content": "pergunta"}]
    result = run_tool_loop(provider, registry_with_lookup(), original)
    assert result.text == "síntese"
    assert provider.contexts[2][:2] == original
    assert [message["tool_call_id"] for message in provider.contexts[2] if message["role"] == "tool"] == ["1", "2"]


def test_iteration_limit_uses_safe_fallback():
    calls = [ProviderTurn(tool_calls=(ToolCall(str(i), "lookup", {"query": "x"}),)) for i in range(3)]
    result = run_tool_loop(ScriptedProvider(*calls), registry_with_lookup(), [], maximum_tool_iterations=2, fallback_text="seguro")
    assert (result.text, result.status, result.iterations) == ("seguro", "iteration_limit", 2)


@pytest.mark.parametrize("turn", [RuntimeError("provider secret"), {"text": "invalid payload"}])
def test_provider_failure_or_invalid_payload_falls_back(turn):
    result = run_tool_loop(ScriptedProvider(turn), registry_with_lookup(), [], fallback_text="seguro")
    assert result.text == "seguro"
    assert result.status == "fallback"


def test_empty_provider_response_falls_back():
    result = run_tool_loop(ScriptedProvider(ProviderTurn()), registry_with_lookup(), [], fallback_text="seguro")
    assert (result.text, result.status) == ("seguro", "fallback")


def test_unknown_tool_error_is_returned_to_provider_for_recovery():
    provider = ScriptedProvider(
        ProviderTurn(tool_calls=(ToolCall("1", "unknown", {}),)),
        ProviderTurn(text="recuperado"),
    )
    result = run_tool_loop(provider, registry_with_lookup(), [])
    assert result.text == "recuperado"
    assert provider.contexts[1][-1]["content"] == "tool not found"
    assert provider.contexts[1][-1]["is_error"] is True
