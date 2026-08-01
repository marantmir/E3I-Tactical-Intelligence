"""Provider-neutral orchestration of bounded, allowlisted LLM tool calls.

Provider-specific wire formats deliberately stop at ``ProviderToolAdapter``.  This
module owns the safe loop and can therefore be exercised without credentials or
network access.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from time import monotonic
from typing import Any, Callable, Protocol, Sequence

from .logging_config import LOGGER_NAME, log_event
from .tool_registry import ToolError, ToolRegistry


@dataclass(frozen=True, slots=True)
class NormalizedToolCall:
    tool_call_id: str
    name: str
    arguments: dict[str, Any] | str


@dataclass(frozen=True, slots=True)
class NormalizedToolResult:
    tool_call_id: str
    name: str
    status: str
    output: Any = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class NormalizedModelResponse:
    content: str | None = None
    tool_calls: tuple[NormalizedToolCall, ...] = ()


@dataclass(frozen=True, slots=True)
class ToolExecutionContext:
    provider: str
    iteration: int


class ProviderToolAdapter(Protocol):
    """Small boundary implemented later by each provider integration."""

    provider: str

    def complete(
        self, messages: Sequence[dict[str, Any]], tools: Sequence[dict[str, Any]]
    ) -> NormalizedModelResponse:
        ...


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    content: str
    history: tuple[dict[str, Any], ...]
    iterations: int
    used_fallback: bool = False


class LLMToolOrchestrator:
    """Run a model/tool loop with strict iteration and registry boundaries."""

    def __init__(
        self,
        adapter: ProviderToolAdapter,
        registry: ToolRegistry,
        *,
        max_iterations: int = 4,
        max_argument_bytes: int = 8_192,
        fallback: Callable[[str], str] | None = None,
    ) -> None:
        if not 1 <= max_iterations <= 8:
            raise ValueError("max_iterations must be between 1 and 8")
        if max_argument_bytes <= 0:
            raise ValueError("max_argument_bytes must be positive")
        self.adapter = adapter
        self.registry = registry
        self.max_iterations = max_iterations
        self.max_argument_bytes = max_argument_bytes
        self.fallback = fallback or (lambda _prompt: "Resposta local indisponível; tente novamente.")
        self._logger = logging.getLogger(LOGGER_NAME)

    def run(
        self, user_message: str, *, history: Sequence[dict[str, Any]] | None = None
    ) -> OrchestrationResult:
        messages = [dict(message) for message in (history or ())]
        messages.append({"role": "user", "content": user_message})

        for iteration in range(1, self.max_iterations + 1):
            try:
                response = self.adapter.complete(tuple(messages), tuple(self.registry.list_definitions()))
            except Exception:
                return self._fallback_result(user_message, messages, iteration)

            if not response.tool_calls:
                if response.content:
                    messages.append({"role": "assistant", "content": response.content})
                    return OrchestrationResult(response.content, tuple(messages), iteration)
                return self._fallback_result(user_message, messages, iteration)

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [self._call_message(call) for call in response.tool_calls],
                }
            )
            for call in response.tool_calls:
                result = self._execute(call, ToolExecutionContext(self.adapter.provider, iteration))
                messages.append({"role": "tool", **self._result_message(result)})

        return self._fallback_result(user_message, messages, self.max_iterations)

    def _execute(self, call: NormalizedToolCall, context: ToolExecutionContext) -> NormalizedToolResult:
        started = monotonic()
        status = "error"
        try:
            arguments = self._normalize_arguments(call.arguments)
            output = self.registry.execute(call.name, arguments)
            status = "success"
            return NormalizedToolResult(call.tool_call_id, call.name, status, output=output)
        except ToolError as exc:
            return NormalizedToolResult(call.tool_call_id, call.name, status, error=str(exc))
        except Exception:
            return NormalizedToolResult(call.tool_call_id, call.name, status, error="Tool call is invalid")
        finally:
            log_event(
                self._logger,
                "llm_tool_orchestration",
                provider=context.provider,
                tool=call.name,
                status=status,
                duration_ms=round((monotonic() - started) * 1000, 2),
            )

    def _normalize_arguments(self, value: dict[str, Any] | str) -> dict[str, Any]:
        encoded = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > self.max_argument_bytes:
            from .tool_registry import ToolSizeLimitError

            raise ToolSizeLimitError("Tool arguments exceed the size limit")
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                from .tool_registry import ToolValidationError

                raise ToolValidationError("Tool arguments are invalid") from exc
        if not isinstance(value, dict):
            from .tool_registry import ToolValidationError

            raise ToolValidationError("Tool arguments must be an object")
        return value

    @staticmethod
    def _call_message(call: NormalizedToolCall) -> dict[str, Any]:
        return {"id": call.tool_call_id, "name": call.name, "arguments": call.arguments}

    @staticmethod
    def _result_message(result: NormalizedToolResult) -> dict[str, Any]:
        return {
            "tool_call_id": result.tool_call_id,
            "name": result.name,
            "status": result.status,
            "content": result.output if result.status == "success" else {"error": result.error},
        }

    def _fallback_result(
        self, prompt: str, messages: list[dict[str, Any]], iterations: int
    ) -> OrchestrationResult:
        content = self.fallback(prompt)
        messages.append({"role": "assistant", "content": content, "fallback": True})
        return OrchestrationResult(content, tuple(messages), iterations, used_fallback=True)
