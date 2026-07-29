"""Central, environment-driven parameters for the intelligence runtime."""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class IntelligenceConfig:
    mode: str = "offline"
    tool_timeout_seconds: float = 12.0
    max_parallel_tools: int = 4
    latency_budget_ms: int = 20_000
    annotate_missing_data: bool = True

    @classmethod
    def from_env(cls) -> "IntelligenceConfig":
        mode = os.getenv("E3I_INTELLIGENCE_MODE", "offline").strip().lower()
        if mode not in {"offline", "online"}:
            mode = "offline"
        return cls(
            mode=mode,
            tool_timeout_seconds=_float_env("E3I_TOOL_TIMEOUT_SECONDS", 12.0, 0.1, 90.0),
            max_parallel_tools=_int_env("E3I_MAX_PARALLEL_TOOLS", 4, 1, 16),
            latency_budget_ms=_int_env("E3I_LATENCY_BUDGET_MS", 20_000, 100, 120_000),
            annotate_missing_data=_bool_env("E3I_ANNOTATE_MISSING_DATA", True),
        )


def _int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def _float_env(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}
