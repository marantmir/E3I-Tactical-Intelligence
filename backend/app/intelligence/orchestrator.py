"""Fail-soft orchestration with offline gating, provenance, and latency traces."""
from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from .config import IntelligenceConfig
from .registry import ToolRegistry


@dataclass
class OrchestrationResult:
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)
    missing_data: list[dict[str, str]] = field(default_factory=list)
    total_latency_ms: float = 0.0


class ToolOrchestrator:
    def __init__(self, registry: ToolRegistry, config: IntelligenceConfig | None = None) -> None:
        self.registry = registry
        self.config = config or IntelligenceConfig.from_env()

    def run(self, plan: list[str], context: dict[str, Any]) -> OrchestrationResult:
        result = OrchestrationResult()
        started = perf_counter()
        for name in plan:
            tool_started = perf_counter()
            try:
                tool = self.registry.get(name)
                if tool.requires_online and self.config.mode == "offline":
                    self._missing(result, name, "tool disabled by offline mode")
                    status = "skipped"
                else:
                    result.outputs[name] = tool.handler(dict(context))
                    status = "ok"
            except Exception as exc:  # tool boundary: one failure must not abort the dossier
                status = "error"
                self._missing(result, name, f"{type(exc).__name__}: {exc}")
            latency_ms = round((perf_counter() - tool_started) * 1000, 3)
            result.traces.append({
                "phase": "P-P-R-L",
                "tool": name,
                "status": status,
                "latency_ms": latency_ms,
                "latency_budget_exceeded": latency_ms > self.config.latency_budget_ms,
            })
        result.total_latency_ms = round((perf_counter() - started) * 1000, 3)
        return result

    def _missing(self, result: OrchestrationResult, tool: str, reason: str) -> None:
        if self.config.annotate_missing_data:
            result.missing_data.append({"tool": tool, "reason": reason, "annotation": "DADO_AUSENTE"})
