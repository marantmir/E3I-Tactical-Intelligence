import json
import logging
import time

import pytest
from pydantic import BaseModel, ConfigDict

from app.tool_registry import (
    ToolDefinition,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistry,
    ToolSizeLimitError,
    ToolTimeoutError,
    ToolValidationError,
    create_default_tool_registry,
)


class EchoInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    value: str


def _definition(execute=lambda arguments: {"value": arguments.value}, **limits):
    return ToolDefinition(
        name="echo",
        description="Echo validated text.",
        input_model=EchoInput,
        execute=execute,
        **limits,
    )


def test_registry_lists_provider_neutral_definition_and_executes_callable():
    registry = ToolRegistry(allowed_tools={"echo"})
    registry.register(_definition())

    assert registry.list_definitions() == [
        {
            "name": "echo",
            "description": "Echo validated text.",
            "input_schema": EchoInput.model_json_schema(),
        }
    ]
    assert registry.execute("echo", {"value": "validated"}) == {"value": "validated"}


def test_registry_rejects_unknown_and_non_allowlisted_tools():
    registry = ToolRegistry(allowed_tools={"echo"})

    with pytest.raises(ValueError, match="allowlist"):
        registry.register(ToolDefinition("other", "No", EchoInput, lambda value: value))
    with pytest.raises(ToolNotFoundError, match="not available"):
        registry.execute("os.system", {"value": "ignored"})


@pytest.mark.parametrize("arguments", [{}, {"value": 12}, {"value": "ok", "secret": "no"}, "bad"])
def test_registry_validates_arguments(arguments):
    registry = ToolRegistry()
    registry.register(_definition())

    with pytest.raises(ToolValidationError, match="invalid|object"):
        registry.execute("echo", arguments)


def test_registry_enforces_input_and_output_size_limits():
    registry = ToolRegistry()
    registry.register(_definition(max_input_bytes=20, max_output_bytes=20))

    with pytest.raises(ToolSizeLimitError, match="arguments"):
        registry.execute("echo", {"value": "x" * 30})

    output_registry = ToolRegistry()
    output_registry.register(_definition(lambda _: {"value": "x" * 30}, max_output_bytes=20))
    with pytest.raises(ToolSizeLimitError, match="result"):
        output_registry.execute("echo", {"value": "ok"})


def test_registry_times_out_slow_tool():
    registry = ToolRegistry()
    registry.register(_definition(lambda _: time.sleep(0.1), timeout_seconds=0.01))

    with pytest.raises(ToolTimeoutError, match="timed out"):
        registry.execute("echo", {"value": "ok"})


def test_registry_sanitizes_service_errors_and_logs_no_arguments(caplog):
    registry = ToolRegistry()
    registry.register(_definition(lambda _: (_ for _ in ()).throw(RuntimeError("token=super-secret"))))

    with caplog.at_level(logging.INFO, logger="e3i"):
        with pytest.raises(ToolExecutionError, match="Tool execution failed") as captured:
            registry.execute("echo", {"value": "private-value"})

    assert "super-secret" not in str(captured.value)
    logs = " ".join(record.getMessage() + json.dumps(getattr(record, "extra_fields", {})) for record in caplog.records)
    assert "private-value" not in logs
    assert "super-secret" not in logs


def test_default_registry_exposes_only_safe_existing_status_service(monkeypatch):
    monkeypatch.setattr("app.tool_registry.llm_status", lambda: {"enabled": False, "has_api_key": False})
    registry = create_default_tool_registry()

    assert [item["name"] for item in registry.list_definitions()] == ["get_llm_status"]
    assert registry.execute("get_llm_status", {}) == {"enabled": False, "has_api_key": False}
    with pytest.raises(ToolValidationError):
        registry.execute("get_llm_status", {"api_key": "should-not-be-accepted"})
