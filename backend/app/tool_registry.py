"""Provider-neutral, bounded execution for explicitly registered LLM tools."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
import json
import logging
import re
from time import monotonic
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, ValidationError

from .llm_assistant import llm_status
from .logging_config import LOGGER_NAME, log_event
from .tactical_tools import (
    OperationalResearchInput, TacticalSearchInput, TeamInput, VisionInput,
    analyze_video_frames, calculate_tactical_metrics, extract_tactical_ocr,
    get_team_context, run_operational_research, search_tactical_information,
)


_TOOL_NAME = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ToolError(Exception):
    """Safe base exception whose message may be returned to a caller."""


class ToolNotFoundError(ToolError):
    pass


class ToolValidationError(ToolError):
    pass


class ToolTimeoutError(ToolError):
    pass


class ToolSizeLimitError(ToolError):
    pass


class ToolExecutionError(ToolError):
    pass


class EmptyToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    input_model: type[BaseModel]
    execute: Callable[[BaseModel], Any]
    timeout_seconds: float = 5.0
    max_input_bytes: int = 8_192
    max_output_bytes: int = 65_536

    @property
    def input_schema(self) -> dict[str, Any]:
        return self.input_model.model_json_schema()

    def public_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    """Allowlist registry; execution is possible only through stored callables."""

    def __init__(self, *, allowed_tools: set[str] | None = None) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._allowed_tools = frozenset(allowed_tools) if allowed_tools is not None else None
        self._logger = logging.getLogger(LOGGER_NAME)

    def register(self, definition: ToolDefinition) -> None:
        if not _TOOL_NAME.fullmatch(definition.name):
            raise ValueError("Tool name must use lowercase letters, numbers, and underscores")
        if self._allowed_tools is not None and definition.name not in self._allowed_tools:
            raise ValueError("Tool is not in the configured allowlist")
        if definition.name in self._tools:
            raise ValueError("Tool is already registered")
        if definition.timeout_seconds <= 0 or definition.max_input_bytes <= 0 or definition.max_output_bytes <= 0:
            raise ValueError("Tool limits must be positive")
        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except (KeyError, TypeError) as exc:
            raise ToolNotFoundError("Tool is not available") from exc

    def list_definitions(self) -> list[dict[str, Any]]:
        return [self._tools[name].public_definition() for name in sorted(self._tools)]

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        definition = self.get(name)
        started = monotonic()
        status = "error"
        try:
            if not isinstance(arguments, dict):
                raise ToolValidationError("Tool arguments must be an object")
            self._check_size(arguments, definition.max_input_bytes, "Tool arguments exceed the size limit")
            try:
                validated = definition.input_model.model_validate(arguments)
            except ValidationError as exc:
                raise ToolValidationError("Tool arguments are invalid") from exc

            executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"tool-{definition.name}")
            future = executor.submit(definition.execute, validated)
            try:
                result = future.result(timeout=definition.timeout_seconds)
            except FutureTimeoutError as exc:
                future.cancel()
                raise ToolTimeoutError("Tool execution timed out") from exc
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

            self._check_size(result, definition.max_output_bytes, "Tool result exceeds the size limit")
            status = "success"
            return result
        except ToolError:
            raise
        except Exception as exc:
            # Deliberately omit exception messages: services may include secrets in them.
            raise ToolExecutionError("Tool execution failed") from exc
        finally:
            log_event(
                self._logger,
                "llm_tool_execution",
                tool=definition.name,
                status=status,
                duration_ms=round((monotonic() - started) * 1000, 2),
            )

    @staticmethod
    def _check_size(value: Any, maximum: int, message: str) -> None:
        try:
            encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError, OverflowError) as exc:
            raise ToolValidationError("Tool data is not serializable") from exc
        if len(encoded) > maximum:
            raise ToolSizeLimitError(message)


def _get_llm_status(_: EmptyToolInput) -> dict[str, Any]:
    return llm_status()


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry(allowed_tools={
        "get_llm_status", "search_tactical_information", "extract_tactical_ocr",
        "analyze_video_frames", "calculate_tactical_metrics",
        "run_operational_research", "get_team_context",
    })
    registry.register(
        ToolDefinition(
            name="get_llm_status",
            description="Return the configured LLM runtime status without credentials.",
            input_model=EmptyToolInput,
            execute=_get_llm_status,
            timeout_seconds=2.0,
            max_input_bytes=256,
            max_output_bytes=4_096,
        )
    )
    definitions = (
        ("search_tactical_information", "Search and rank public tactical sources.", TacticalSearchInput, search_tactical_information, 15.0, 8_192, 65_536),
        ("extract_tactical_ocr", "Interpret visible tactical text in supplied frame observations.", VisionInput, extract_tactical_ocr, 12.0, 131_072, 65_536),
        ("analyze_video_frames", "Analyze supplied computer-vision frame observations.", VisionInput, analyze_video_frames, 12.0, 131_072, 65_536),
        ("calculate_tactical_metrics", "Calculate projected graph metrics for a registered team.", TeamInput, calculate_tactical_metrics, 5.0, 512, 16_384),
        ("run_operational_research", "Optimize a registered squad against formation scenarios.", OperationalResearchInput, run_operational_research, 8.0, 1_024, 131_072),
        ("get_team_context", "Return sanitized context for a registered team.", TeamInput, get_team_context, 3.0, 512, 65_536),
    )
    for name, description, model, execute, timeout, max_input, max_output in definitions:
        registry.register(ToolDefinition(name, description, model, execute, timeout, max_input, max_output))
    return registry
