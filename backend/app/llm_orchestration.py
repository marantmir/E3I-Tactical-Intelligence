"""Provider-neutral, bounded tool-calling loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .llm_tools import ToolError, ToolRegistry


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: Any


@dataclass(frozen=True)
class ProviderTurn:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)


class ToolCallingProvider(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ProviderTurn: ...


@dataclass(frozen=True)
class OrchestrationResult:
    text: str
    status: str
    iterations: int
    messages: tuple[dict[str, Any], ...]


def run_tool_loop(
    provider: ToolCallingProvider,
    registry: ToolRegistry,
    messages: list[dict[str, Any]],
    *,
    maximum_tool_iterations: int = 4,
    tool_timeout_seconds: float = 5.0,
    maximum_tool_result_chars: int = 12_000,
    fallback_text: str = "Não foi possível concluir a análise com segurança.",
) -> OrchestrationResult:
    """Run sequential provider turns while preserving the complete local context."""
    context = [dict(message) for message in messages]
    if maximum_tool_iterations < 0:
        raise ValueError("maximum_tool_iterations must be non-negative")

    for iteration in range(maximum_tool_iterations + 1):
        try:
            turn = provider.complete(context, registry.definitions())
        except Exception:
            return OrchestrationResult(fallback_text, "fallback", iteration, tuple(context))
        if not isinstance(turn, ProviderTurn):
            return OrchestrationResult(fallback_text, "fallback", iteration, tuple(context))
        if not turn.tool_calls:
            text = turn.text.strip()
            return OrchestrationResult(text or fallback_text, "completed" if text else "fallback", iteration, tuple(context))
        if iteration == maximum_tool_iterations:
            return OrchestrationResult(fallback_text, "iteration_limit", iteration, tuple(context))

        context.append(
            {
                "role": "assistant",
                "content": turn.text,
                "tool_calls": [
                    {"id": call.id, "name": call.name, "arguments": call.arguments} for call in turn.tool_calls
                ],
            }
        )
        for call in turn.tool_calls:
            try:
                output = registry.execute(call.name, call.arguments, timeout_seconds=tool_timeout_seconds)
                if len(output) > maximum_tool_result_chars:
                    output = output[:maximum_tool_result_chars] + "…[truncated]"
                is_error = False
            except ToolError as error:
                output = str(error)
                is_error = True
            context.append(
                {"role": "tool", "tool_call_id": call.id, "name": call.name, "content": output, "is_error": is_error}
            )

    return OrchestrationResult(fallback_text, "iteration_limit", maximum_tool_iterations, tuple(context))
