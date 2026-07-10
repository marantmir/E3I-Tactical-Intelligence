from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "llm_config.json"

DEFAULT_LLM_CONFIG = {
    "enabled": False,
    "provider": "openai_responses",
    "model": "gpt-4.1-mini",
    "timeout_seconds": 18,
    "temperature": 0.2,
    "max_output_tokens": 1400,
    "language": "pt-BR",
    "analysis_depth": "profunda",
    "search_scope": "tactical_visual_only",
    "identity_mode": "strict_visual_evidence",
    "api_key": "",
}


def get_llm_runtime_config() -> dict:
    config = _read_config()
    env_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    env_model = os.getenv("OPENAI_MODEL", "").strip()
    env_timeout = os.getenv("E3I_LLM_TIMEOUT_SECONDS", "").strip()

    if env_api_key:
        config["api_key"] = env_api_key
        config["api_key_source"] = "env"
    else:
        config["api_key_source"] = "local_config" if config.get("api_key") else "missing"

    if env_model:
        config["model"] = env_model
    if env_timeout.isdigit():
        config["timeout_seconds"] = _clamp_int(env_timeout, 3, 90)

    return config


def public_llm_config() -> dict:
    config = get_llm_runtime_config()
    has_key = bool(config.get("api_key"))
    return {
        "enabled": bool(config.get("enabled")),
        "provider": config.get("provider") or "openai_responses",
        "model": config.get("model") or DEFAULT_LLM_CONFIG["model"],
        "timeout_seconds": config.get("timeout_seconds") or DEFAULT_LLM_CONFIG["timeout_seconds"],
        "temperature": config.get("temperature"),
        "max_output_tokens": config.get("max_output_tokens"),
        "language": config.get("language"),
        "analysis_depth": config.get("analysis_depth"),
        "search_scope": config.get("search_scope"),
        "identity_mode": config.get("identity_mode"),
        "has_api_key": has_key,
        "api_key_source": config.get("api_key_source") or "missing",
        "api_key_mask": _mask_key(config.get("api_key", "")) if has_key else "",
    }


def save_llm_config(payload: dict) -> dict:
    current = _read_config()
    next_config = deepcopy(current)

    for key in (
        "enabled",
        "provider",
        "model",
        "language",
        "analysis_depth",
        "search_scope",
        "identity_mode",
    ):
        if key in payload and payload[key] is not None:
            next_config[key] = _clean_text(payload[key]) if isinstance(payload[key], str) else payload[key]

    if "timeout_seconds" in payload and payload["timeout_seconds"] is not None:
        next_config["timeout_seconds"] = _clamp_int(payload["timeout_seconds"], 3, 90)
    if "temperature" in payload and payload["temperature"] is not None:
        next_config["temperature"] = _clamp_float(payload["temperature"], 0, 1)
    if "max_output_tokens" in payload and payload["max_output_tokens"] is not None:
        next_config["max_output_tokens"] = _clamp_int(payload["max_output_tokens"], 256, 6000)

    if payload.get("clear_api_key"):
        next_config["api_key"] = ""
    elif payload.get("api_key"):
        next_config["api_key"] = str(payload["api_key"]).strip()

    if next_config.get("provider") != "openai_responses":
        next_config["provider"] = "openai_responses"
    if not next_config.get("model"):
        next_config["model"] = DEFAULT_LLM_CONFIG["model"]

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(next_config, ensure_ascii=False, indent=2), encoding="utf-8")
    return public_llm_config()


def _read_config() -> dict:
    config = deepcopy(DEFAULT_LLM_CONFIG)
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                config.update(saved)
        except (OSError, json.JSONDecodeError):
            pass
    return config


def _mask_key(value: str) -> str:
    if len(value) <= 8:
        return "********"
    return f"{value[:4]}...{value[-4:]}"


def _clean_text(value) -> str:
    return " ".join(str(value or "").strip().split())


def _clamp_int(value, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum
    return max(minimum, min(maximum, number))


def _clamp_float(value, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = minimum
    return max(minimum, min(maximum, number))
