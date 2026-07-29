"""Adapters for Search, OCR, Video, and Metrics; dependencies are injected for API mocking."""
from __future__ import annotations

from typing import Any, Callable

from .registry import ToolDefinition, ToolRegistry


def build_default_registry(
    *,
    search: Callable[[dict[str, Any]], dict[str, Any]],
    ocr: Callable[[dict[str, Any]], dict[str, Any]],
    video: Callable[[dict[str, Any]], dict[str, Any]],
    metrics: Callable[[dict[str, Any]], dict[str, Any]],
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolDefinition("search", search, True, "Collect public tactical evidence"))
    registry.register(ToolDefinition("ocr", ocr, False, "Read jersey text/numbers from supplied crops"))
    registry.register(ToolDefinition("video", video, False, "Extract visual events and movement tracks"))
    registry.register(ToolDefinition("metrics", metrics, False, "Calculate tactical graph and team metrics"))
    return registry
