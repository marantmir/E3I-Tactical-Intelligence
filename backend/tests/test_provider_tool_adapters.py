import pytest

from app.provider_tool_adapters import (
    FallbackProviderAdapter, FinOpsConfig, PROVIDER_CAPABILITIES,
    ProviderRequestError, ProviderToolAdapter,
)


PROVIDERS = tuple(PROVIDER_CAPABILITIES)
TOOLS = ({"name": "lookup", "description": "Lookup", "input_schema": {"type": "object", "properties": {"q": {"type": "string"}}}},)


class MockTransport:
    def __init__(self, *responses): self.responses, self.calls = list(responses), []
    def send(self, provider, payload, *, timeout):
        self.calls.append((provider, payload, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception): raise response
        return response


def response(provider, *, call=False, text="final"):
    if provider == "openai_responses":
        return {"output": [{"type": "function_call", "call_id": "c1", "name": "lookup", "arguments": '{"q":"x"}'}]} if call else {"output_text": text}
    if provider == "anthropic_messages":
        return {"content": [{"type": "tool_use", "id": "c1", "name": "lookup", "input": {"q": "x"}}]} if call else {"content": [{"type": "text", "text": text}]}
    if provider == "google_gemini":
        part = {"functionCall": {"id": "c1", "name": "lookup", "args": {"q": "x"}}} if call else {"text": text}
        return {"candidates": [{"content": {"parts": [part]}}]}
    message = {"tool_calls": [{"id": "c1", "function": {"name": "lookup", "arguments": '{"q":"x"}'}}]} if call else {"content": text}
    return {"choices": [{"message": message}]}


def adapter(provider, transport, **overrides):
    values = dict(provider=provider, model=f"{provider}-model", temperature=.2, top_p=.8, seed=7, max_output_tokens=99, timeout_seconds=2, retries=0)
    values.update(overrides)
    return ProviderToolAdapter(provider, "mock-key", FinOpsConfig(**values), transport)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_text_payload_and_final_response(provider):
    transport = MockTransport(response(provider))
    result = adapter(provider, transport).complete(({"role": "user", "content": "hello"},), ())
    assert result.content == "final"
    assert "hello" in str(transport.calls[0][1])
    assert transport.calls[0][2] == 2


@pytest.mark.parametrize("provider", PROVIDERS)
def test_multimodal_payload_preserves_text_and_image(provider):
    transport = MockTransport(response(provider))
    message = {"role": "user", "content": [{"type": "text", "text": "frame"}, {"type": "image", "media_type": "image/png", "data": "YWJj"}]}
    adapter(provider, transport).complete((message,), ())
    payload = str(transport.calls[0][1])
    assert "frame" in payload and "YWJj" in payload and "image/png" in payload


@pytest.mark.parametrize("provider", PROVIDERS)
def test_tools_are_serialized_and_calls_normalized(provider):
    transport = MockTransport(response(provider, call=True))
    result = adapter(provider, transport).complete(({"role": "user", "content": "use tool"},), TOOLS)
    assert "lookup" in str(transport.calls[0][1])
    assert result.tool_calls[0].tool_call_id == "c1"
    assert result.tool_calls[0].name == "lookup"


@pytest.mark.parametrize("provider", PROVIDERS)
def test_native_tool_result_is_returned_then_final_response(provider):
    transport = MockTransport(response(provider))
    history = ({"role": "user", "content": "x"}, {"role": "assistant", "content": None, "tool_calls": [{"id": "c1", "name": "lookup", "arguments": {"q": "x"}}]}, {"role": "tool", "tool_call_id": "c1", "name": "lookup", "content": {"answer": 1}})
    result = adapter(provider, transport).complete(history, TOOLS)
    assert result.content == "final"
    payload = str(transport.calls[0][1])
    assert "answer" in payload
    assert PROVIDER_CAPABILITIES[provider].tool_result_format


@pytest.mark.parametrize("provider", PROVIDERS)
def test_only_compatible_parameters_are_sent(provider):
    transport = MockTransport(response(provider))
    adapter(provider, transport).complete(({"role": "user", "content": "x"},), ())
    payload = transport.calls[0][1]
    serialized = str(payload)
    assert "temperature" in serialized
    assert ("seed" in serialized) is PROVIDER_CAPABILITIES[provider].seed
    assert "max" in serialized.lower()


@pytest.mark.parametrize("provider", PROVIDERS)
def test_absent_credential_makes_no_request(provider):
    transport = MockTransport(response(provider))
    item = ProviderToolAdapter(provider, "", FinOpsConfig(provider=provider), transport)
    with pytest.raises(ProviderRequestError, match="credential"): item.complete((), ())
    assert transport.calls == []


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("kind", ["timeout", "temporary", "rate_limit"])
def test_transient_failures_retry(provider, kind):
    transport = MockTransport(ProviderRequestError(kind), response(provider))
    result = adapter(provider, transport, retries=1).complete(({"role": "user", "content": "x"},), ())
    assert result.content == "final" and len(transport.calls) == 2


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("kind", ["authentication", "invalid_argument", "safety_block", "invalid_schema"])
def test_non_transient_failures_are_not_retried(provider, kind):
    transport = MockTransport(ProviderRequestError(kind), response(provider))
    with pytest.raises(ProviderRequestError) as caught:
        adapter(provider, transport, retries=2).complete(({"role": "user", "content": "x"},), ())
    assert caught.value.kind == kind and len(transport.calls) == 1


def test_fallback_between_mocked_providers_preserves_context_and_records_route():
    first_transport = MockTransport(ProviderRequestError("timeout"))
    second_transport = MockTransport(response("anthropic_messages", text="second"))
    adapters = {"openai_responses": adapter("openai_responses", first_transport), "anthropic_messages": adapter("anthropic_messages", second_transport)}
    fallback = FallbackProviderAdapter(adapters, ("openai_responses", "anthropic_messages"), 2, lambda _: "local")
    messages = ({"role": "system", "content": "safe"}, {"role": "user", "content": "question"})
    assert fallback.complete(messages, TOOLS).content == "second"
    assert fallback.initial_provider == "openai_responses" and fallback.final_provider == "anthropic_messages"
    assert "safe" in str(second_transport.calls[0][1]) and "question" in str(second_transport.calls[0][1])


def test_fallback_is_disabled_by_empty_order_and_uses_local_without_paid_call():
    transport = MockTransport(response("openai_responses"))
    fallback = FallbackProviderAdapter({"openai_responses": adapter("openai_responses", transport)}, (), 2, lambda messages: "local:" + messages[-1]["content"])
    assert fallback.complete(({"role": "user", "content": "q"},), TOOLS).content == "local:q"
    assert transport.calls == [] and fallback.final_provider == "deterministic_local"


def test_fallback_skips_missing_credentials_and_honors_attempt_limit():
    missing = ProviderToolAdapter("openai_responses", "", FinOpsConfig(), MockTransport(response("openai_responses")))
    failing_transport = MockTransport(ProviderRequestError("temporary"))
    third_transport = MockTransport(response("google_gemini"))
    fallback = FallbackProviderAdapter({"openai_responses": missing, "anthropic_messages": adapter("anthropic_messages", failing_transport), "google_gemini": adapter("google_gemini", third_transport)}, PROVIDERS, 1, lambda _: "local")
    assert fallback.complete(({"role": "user", "content": "q"},), ()).content == "local"
    assert len(failing_transport.calls) == 1 and third_transport.calls == []


def test_authentication_cause_is_recorded_and_stops_fallback():
    first = MockTransport(ProviderRequestError("authentication"))
    second = MockTransport(response("anthropic_messages"))
    fallback = FallbackProviderAdapter({"openai_responses": adapter("openai_responses", first), "anthropic_messages": adapter("anthropic_messages", second)}, ("openai_responses", "anthropic_messages"), 2, lambda _: "local")
    assert fallback.complete(({"role": "user", "content": "q"},), ()).content == "local"
    assert fallback.causes == [("openai_responses", "authentication")] and second.calls == []
