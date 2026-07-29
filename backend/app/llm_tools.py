"""Registry and bounded execution primitives for local LLM tools.

The registry deliberately accepts only explicitly registered callables.  It is
provider-neutral and never performs network I/O by itself.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
import json
from typing import Any, Callable

from pydantic import BaseModel, ValidationError


class ToolError(Exception):
    """Safe error returned to the model without exposing internal details."""


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    arguments_model: type[BaseModel]
    handler: Callable[..., Any]

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.arguments_model.model_json_schema(),
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        arguments_model: type[BaseModel],
        handler: Callable[..., Any],
    ) -> None:
        normalized = name.strip()
        if not normalized or normalized in self._tools:
            raise ValueError("tool name must be non-empty and unique")
        self._tools[normalized] = ToolDefinition(normalized, description.strip(), arguments_model, handler)

    def definitions(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(self, name: str, arguments: Any, *, timeout_seconds: float = 5.0) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolError("tool not found")
        if not isinstance(arguments, dict):
            raise ToolError("invalid tool arguments")
        try:
            validated = tool.arguments_model.model_validate(arguments)
        except ValidationError as error:
            fields = sorted({str(item["loc"][0]) for item in error.errors() if item.get("loc")})
            suffix = f": {', '.join(fields)}" if fields else ""
            raise ToolError(f"invalid tool arguments{suffix}") from None

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(tool.handler, **validated.model_dump())
        try:
            result = future.result(timeout=max(0.001, timeout_seconds))
        except FutureTimeout:
            future.cancel()
            raise ToolError("tool execution timed out") from None
        except Exception:
            raise ToolError("tool execution failed") from None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        if result is None or result == "" or result == [] or result == {}:
            return "No result available."
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
