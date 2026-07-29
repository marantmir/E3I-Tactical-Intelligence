"""Typed registry for independently testable intelligence tools."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: ToolHandler
    requires_online: bool = False
    description: str = ""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if not definition.name.strip():
            raise ValueError("tool name cannot be empty")
        if definition.name in self._tools:
            raise ValueError(f"tool already registered: {definition.name}")
        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc

    def catalog(self) -> list[dict[str, Any]]:
        return [
            {"name": item.name, "requires_online": item.requires_online, "description": item.description}
            for item in sorted(self._tools.values(), key=lambda item: item.name)
        ]
