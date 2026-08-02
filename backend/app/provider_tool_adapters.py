"""Provider wire adapters, capability filtering, retry and provider fallback.

The module has no SDK dependency and accepts an injected transport.  Production
code may supply an HTTP transport; tests use in-memory transports exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import time
from typing import Any, Callable, Mapping, Protocol, Sequence

from .llm_tool_orchestrator import NormalizedModelResponse, NormalizedToolCall
from .logging_config import LOGGER_NAME, log_event


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    text: bool
    image: bool
    tool_calling: bool
    structured_output: bool
    temperature: bool
    top_p: bool
    seed: bool
    max_tokens: bool
    tool_result_format: str
    parallel_tool_calls: bool
    known_limitations: tuple[str, ...] = ()


PROVIDER_CAPABILITIES: Mapping[str, ProviderCapabilities] = {
    "openai_responses": ProviderCapabilities(True, True, True, True, True, True, False, True, "function_call_output", True, ("Seed is not represented by this Responses adapter.",)),
    "anthropic_messages": ProviderCapabilities(True, True, True, False, True, True, False, True, "tool_result content block", True, ("Native structured-output schema is not represented.", "Seed is unsupported.")),
    "google_gemini": ProviderCapabilities(True, True, True, True, True, True, False, True, "functionResponse part", True, ("Seed is unsupported by this adapter.",)),
    "xai_grok": ProviderCapabilities(True, True, True, True, True, True, True, True, "tool role message", True, ("Image inputs depend on the selected Grok model." ,)),
}


@dataclass(frozen=True, slots=True)
class FinOpsConfig:
    provider: str = "openai_responses"
    model: str = "gpt-4.1-mini"
    temperature: float | None = 0.2
    top_p: float | None = 0.9
    seed: int | None = None
    max_output_tokens: int = 1400
    timeout_seconds: float = 18
    retries: int = 1
    max_iterations: int = 4
    max_tools: int = 16
    max_frames: int = 8
    context_limit_bytes: int = 128_000
    result_limit_bytes: int = 32_000
    fallback_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.retries not in range(0, 4):
            raise ValueError("retries must be between 0 and 3")
        if not 1 <= self.max_iterations <= 8 or self.max_tools <= 0:
            raise ValueError("invalid orchestration limits")


class ProviderRequestError(RuntimeError):
    """Sanitized provider failure with retry/fallback classification."""

    TRANSIENT = frozenset({"timeout", "temporary", "rate_limit"})

    def __init__(self, kind: str, message: str = "Provider request failed") -> None:
        super().__init__(message)
        self.kind = kind

    @property
    def transient(self) -> bool:
        return self.kind in self.TRANSIENT


class ProviderTransport(Protocol):
    def send(self, provider: str, payload: dict[str, Any], *, timeout: float) -> dict[str, Any]: ...


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _parts(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return list(content or [])


class ProviderToolAdapter:
    """Serialize a normalized conversation to one provider's native format."""

    def __init__(self, provider: str, api_key: str, config: FinOpsConfig, transport: ProviderTransport) -> None:
        if provider not in PROVIDER_CAPABILITIES:
            raise ValueError("unsupported provider")
        self.provider, self.api_key, self.config, self.transport = provider, api_key.strip(), config, transport
        self.capabilities = PROVIDER_CAPABILITIES[provider]
        self.last_payload: dict[str, Any] | None = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def complete(self, messages: Sequence[dict[str, Any]], tools: Sequence[dict[str, Any]]) -> NormalizedModelResponse:
        if not self.configured:
            raise ProviderRequestError("missing_credential", "Provider credential is missing")
        payload = self._payload(messages, tools[: self.config.max_tools])
        if len(_json(payload).encode()) > self.config.context_limit_bytes:
            raise ProviderRequestError("invalid_argument", "Context limit exceeded")
        self.last_payload = payload
        for attempt in range(self.config.retries + 1):
            try:
                raw = self.transport.send(self.provider, payload, timeout=self.config.timeout_seconds)
                return self._parse(raw)
            except ProviderRequestError as exc:
                if not exc.transient or attempt >= self.config.retries:
                    raise
                time.sleep(min(0.01 * (2**attempt), 0.04))
        raise AssertionError("unreachable")

    def _parameters(self, max_key: str) -> dict[str, Any]:
        cap, cfg = self.capabilities, self.config
        values: dict[str, Any] = {max_key: cfg.max_output_tokens}
        if cap.temperature and cfg.temperature is not None: values["temperature"] = cfg.temperature
        if cap.top_p and cfg.top_p is not None: values["top_p"] = cfg.top_p
        if cap.seed and cfg.seed is not None: values["seed"] = cfg.seed
        return values

    def _payload(self, messages: Sequence[dict[str, Any]], tools: Sequence[dict[str, Any]]) -> dict[str, Any]:
        serializers = {
            "openai_responses": self._openai_payload, "anthropic_messages": self._anthropic_payload,
            "google_gemini": self._gemini_payload, "xai_grok": self._grok_payload,
        }
        return serializers[self.provider](messages, tools)

    @staticmethod
    def _functions(tools: Sequence[dict[str, Any]], *, nested: bool = False) -> list[dict[str, Any]]:
        result = []
        for tool in tools:
            function = {"name": tool["name"], "description": tool.get("description", ""), "parameters": tool.get("input_schema", tool.get("parameters", {"type": "object"}))}
            result.append({"type": "function", "function": function} if nested else {"type": "function", **function})
        return result

    def _openai_payload(self, messages, tools):
        items = []
        for msg in messages:
            if msg["role"] == "tool":
                items.append({"type": "function_call_output", "call_id": msg["tool_call_id"], "output": _json(msg["content"])})
                continue
            content = []
            for part in _parts(msg.get("content")):
                if part["type"] == "text": content.append({"type": "input_text", "text": part["text"]})
                elif part["type"] == "image": content.append({"type": "input_image", "image_url": part.get("url") or f"data:{part.get('media_type','image/jpeg')};base64,{part['data']}"})
            items.append({"role": msg["role"], "content": content})
            for call in msg.get("tool_calls", []): items.append({"type": "function_call", "call_id": call["id"], "name": call["name"], "arguments": _json(call["arguments"]) if isinstance(call["arguments"], dict) else call["arguments"]})
        return {"model": self.config.model, "input": items, "tools": self._functions(tools), **self._parameters("max_output_tokens")}

    def _anthropic_payload(self, messages, tools):
        system, output = [], []
        for msg in messages:
            if msg["role"] == "system": system.extend(p["text"] for p in _parts(msg.get("content")) if p["type"] == "text"); continue
            blocks = []
            if msg["role"] == "tool": blocks = [{"type": "tool_result", "tool_use_id": msg["tool_call_id"], "content": _json(msg["content"])}]
            else:
                for part in _parts(msg.get("content")):
                    if part["type"] == "text": blocks.append({"type": "text", "text": part["text"]})
                    elif part["type"] == "image": blocks.append({"type": "image", "source": {"type": "base64", "media_type": part.get("media_type", "image/jpeg"), "data": part["data"]}})
                blocks += [{"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["arguments"]} for c in msg.get("tool_calls", [])]
            output.append({"role": "user" if msg["role"] == "tool" else msg["role"], "content": blocks})
        return {"model": self.config.model, "system": "\n".join(system), "messages": output, "tools": [{"name": t["name"], "description": t.get("description", ""), "input_schema": t.get("input_schema", {})} for t in tools], **self._parameters("max_tokens")}

    def _gemini_payload(self, messages, tools):
        contents, system = [], []
        for msg in messages:
            if msg["role"] == "system": system.extend({"text": p["text"]} for p in _parts(msg.get("content")) if p["type"] == "text"); continue
            parts = []
            if msg["role"] == "tool": parts.append({"functionResponse": {"name": msg["name"], "response": msg["content"]}})
            else:
                for part in _parts(msg.get("content")):
                    if part["type"] == "text": parts.append({"text": part["text"]})
                    elif part["type"] == "image": parts.append({"inlineData": {"mimeType": part.get("media_type", "image/jpeg"), "data": part["data"]}})
                parts += [{"functionCall": {"name": c["name"], "args": c["arguments"], "id": c["id"]}} for c in msg.get("tool_calls", [])]
            contents.append({"role": "model" if msg["role"] == "assistant" else "user", "parts": parts})
        declarations = [{"name": t["name"], "description": t.get("description", ""), "parameters": t.get("input_schema", {})} for t in tools]
        payload = {"model": self.config.model, "contents": contents, "tools": [{"functionDeclarations": declarations}], "generationConfig": self._parameters("maxOutputTokens")}
        if system: payload["systemInstruction"] = {"parts": system}
        payload["generationConfig"] = {{"top_p": "topP"}.get(k, k): v for k, v in payload["generationConfig"].items()}
        return payload

    def _grok_payload(self, messages, tools):
        output = []
        for msg in messages:
            native = {"role": msg["role"]}
            if msg["role"] == "tool": native.update({"tool_call_id": msg["tool_call_id"], "name": msg["name"], "content": _json(msg["content"])})
            else:
                blocks = [{"type": "text", "text": p["text"]} if p["type"] == "text" else {"type": "image_url", "image_url": {"url": p.get("url") or f"data:{p.get('media_type','image/jpeg')};base64,{p['data']}"}} for p in _parts(msg.get("content"))]
                native["content"] = blocks
                if msg.get("tool_calls"): native["tool_calls"] = [{"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": _json(c["arguments"])}} for c in msg["tool_calls"]]
            output.append(native)
        return {"model": self.config.model, "messages": output, "tools": self._functions(tools, nested=True), **self._parameters("max_tokens")}

    def _parse(self, raw: dict[str, Any]) -> NormalizedModelResponse:
        if self.provider == "openai_responses":
            blocks = raw.get("output", []); text = "".join(b.get("text", "") for b in blocks if b.get("type") in {"message", "output_text"}) or raw.get("output_text", "")
            calls = [NormalizedToolCall(b.get("call_id", b.get("id", "")), b["name"], b.get("arguments", {})) for b in blocks if b.get("type") == "function_call"]
        elif self.provider == "anthropic_messages":
            blocks = raw.get("content", []); text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            calls = [NormalizedToolCall(b["id"], b["name"], b.get("input", {})) for b in blocks if b.get("type") == "tool_use"]
        elif self.provider == "google_gemini":
            blocks = ((raw.get("candidates") or [{}])[0].get("content") or {}).get("parts", []); text = "".join(b.get("text", "") for b in blocks)
            calls = [NormalizedToolCall(b["functionCall"].get("id", f"gemini-{i}"), b["functionCall"]["name"], b["functionCall"].get("args", {})) for i, b in enumerate(blocks) if "functionCall" in b]
        else:
            message = ((raw.get("choices") or [{}])[0].get("message") or {}); text = message.get("content") or ""
            calls = [NormalizedToolCall(c["id"], c["function"]["name"], c["function"].get("arguments", {})) for c in message.get("tool_calls", [])]
        return NormalizedModelResponse(text or None, tuple(calls))


@dataclass(slots=True)
class FallbackProviderAdapter:
    """Try configured credentialed providers in order, then deterministic local."""
    adapters: Mapping[str, ProviderToolAdapter]
    order: Sequence[str]
    max_attempts: int
    local_response: Callable[[Sequence[dict[str, Any]]], str]
    provider: str = "provider_fallback"
    initial_provider: str | None = None
    final_provider: str | None = None
    causes: list[tuple[str, str]] = field(default_factory=list)

    def complete(self, messages, tools) -> NormalizedModelResponse:
        logger = logging.getLogger(LOGGER_NAME); attempts = 0
        eligible = [name for name in self.order if name in self.adapters and self.adapters[name].configured]
        self.initial_provider = eligible[0] if eligible else "deterministic_local"
        for name in eligible:
            if attempts >= self.max_attempts: break
            attempts += 1
            try:
                result = self.adapters[name].complete(messages, tools); self.final_provider = name
                log_event(logger, "llm_provider_selection", initial_provider=self.initial_provider, final_provider=name, attempts=attempts)
                return result
            except ProviderRequestError as exc:
                self.causes.append((name, exc.kind))
                log_event(logger, "llm_provider_failure", provider=name, cause=exc.kind)
                if not exc.transient: break
        self.final_provider = "deterministic_local"
        log_event(logger, "llm_provider_selection", initial_provider=self.initial_provider, final_provider=self.final_provider, attempts=attempts)
        return NormalizedModelResponse(content=self.local_response(messages))
