from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "llm_config.json"

# Provedores suportados. Cada um tem sua propria API, formato de autenticacao
# e variavel de ambiente para a chave - a UI deixa o usuario trocar livremente
# entre eles em vez de ficar preso ao provedor parametrizado por padrao.
SUPPORTED_PROVIDERS = ("openai_responses", "anthropic_messages", "google_gemini", "xai_grok")

PROVIDER_LABELS = {
    "openai_responses": "OpenAI (Responses API)",
    "anthropic_messages": "Anthropic Claude (Messages API)",
    "google_gemini": "Google Gemini",
    "xai_grok": "xAI Grok",
}

PROVIDER_DEFAULT_MODELS = {
    "openai_responses": "gpt-4.1-mini",
    "anthropic_messages": "claude-sonnet-5",
    "google_gemini": "gemini-2.5-flash",
    "xai_grok": "grok-4",
}

PROVIDER_MODEL_SUGGESTIONS = {
    "openai_responses": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
    "anthropic_messages": ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5-20251001"],
    "google_gemini": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "xai_grok": ["grok-4", "grok-4-fast", "grok-3-mini"],
}

PROVIDER_ENV_API_KEY = {
    "openai_responses": "OPENAI_API_KEY",
    "anthropic_messages": "ANTHROPIC_API_KEY",
    "google_gemini": "GEMINI_API_KEY",
    "xai_grok": "XAI_API_KEY",
}

PROVIDER_ENV_MODEL = {
    "openai_responses": "OPENAI_MODEL",
    "anthropic_messages": "ANTHROPIC_MODEL",
    "google_gemini": "GEMINI_MODEL",
    "xai_grok": "XAI_MODEL",
}

DEFAULT_LLM_CONFIG = {
    "enabled": False,
    "provider": "openai_responses",
    "model": PROVIDER_DEFAULT_MODELS["openai_responses"],
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
    provider = config.get("provider") or DEFAULT_LLM_CONFIG["provider"]
    if provider not in SUPPORTED_PROVIDERS:
        provider = DEFAULT_LLM_CONFIG["provider"]

    env_api_key = os.getenv(PROVIDER_ENV_API_KEY.get(provider, ""), "").strip()
    env_model = os.getenv(PROVIDER_ENV_MODEL.get(provider, ""), "").strip()
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
        next_config["max_output_tokens"] = _clamp_int(payload["max_output_tokens"], 200, 6000)

    if payload.get("clear_api_key"):
        next_config["api_key"] = ""
    elif payload.get("api_key"):
        next_config["api_key"] = str(payload["api_key"]).strip()

    # Provedor escolhido pelo usuario e respeitado (nao existe mais um
    # provedor unico parametrizado); so cai no padrao se vier algo
    # desconhecido/invalido.
    if next_config.get("provider") not in SUPPORTED_PROVIDERS:
        next_config["provider"] = DEFAULT_LLM_CONFIG["provider"]

    provider_changed = next_config["provider"] != current.get("provider")
    model_explicitly_set = bool(payload.get("model"))
    if not model_explicitly_set and provider_changed:
        # Trocar de provedor sem informar um modelo novo nao pode deixar o
        # modelo do provedor anterior (ex.: "gpt-4.1-mini" com Anthropic
        # selecionado); a UI ja resolve isso ao trocar o select, mas a API
        # precisa ser correta mesmo com um PATCH parcial direto.
        next_config["model"] = PROVIDER_DEFAULT_MODELS.get(next_config["provider"], DEFAULT_LLM_CONFIG["model"])
    elif not next_config.get("model"):
        next_config["model"] = PROVIDER_DEFAULT_MODELS.get(next_config["provider"], DEFAULT_LLM_CONFIG["model"])

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
