import json

import pytest
from pydantic import ValidationError

from app.provider_tool_adapters import FinOpsConfig, ProviderToolAdapter
from app.structured_llm import RUNTIME_SYSTEM_PROMPT, StructuredAnalysis, parse_structured_response


def valid_payload():
    return {
        "summary": "Bloco médio observado.",
        "findings": [{"statement": "Bloco médio", "kind": "fact", "evidence_ids": ["e1"]}],
        "evidence": [{"id": "e1", "source": "text", "description": "bloco médio", "reference": "relatório 60m"}],
        "confidence": {"score": 0.8, "level": "high", "rationale": "fonte direta"},
        "limitations": [{"description": "Sem vídeo", "impact": "medium"}],
        "recommendations": [{"action": "Revisar vídeo", "priority": "medium", "evidence_ids": ["e1"]}],
    }


def test_valid_json_and_markdown_json():
    raw = json.dumps(valid_payload())
    assert parse_structured_response(raw)[1] is False
    assert parse_structured_response(f"```json\n{raw}\n```")[1] is False


@pytest.mark.parametrize("mutation", [
    lambda p: p.pop("summary"),
    lambda p: p.update(summary=4),
    lambda p: p.update(confidence={"score": 4, "level": "high", "rationale": "x"}),
])
def test_missing_wrong_type_and_out_of_range_rejected(mutation):
    payload = valid_payload(); mutation(payload)
    assert parse_structured_response(json.dumps(payload))[1] is True


@pytest.mark.parametrize("raw", ["arbitrary prose", '{"summary":', "x" * 32_001])
def test_incomplete_text_and_large_response_fall_back(raw):
    response, fallback = parse_structured_response(raw)
    assert fallback and response.confidence.score == 0 and not response.evidence


def test_insufficient_evidence_cannot_claim_certainty():
    payload = valid_payload(); payload["evidence"] = []
    assert parse_structured_response(json.dumps(payload))[1] is True


def test_multimodal_conflict_is_valid_at_reduced_confidence():
    payload = valid_payload()
    payload["evidence"] += [{"id": "e2", "source": "metric", "description": "bloco baixo", "reference": "metric"}]
    payload["findings"][0] = {"statement": "Conflito sem conclusão", "kind": "fact", "evidence_ids": ["e1", "e2"]}
    payload["confidence"] = {"score": .3, "level": "low", "rationale": "conflito multimodal"}
    assert parse_structured_response(json.dumps(payload))[1] is False


def test_single_successful_repair_and_single_failed_repair():
    calls = []
    def good(raw, error): calls.append((raw, error)); return json.dumps(valid_payload())
    assert parse_structured_response("bad", repair=good)[1] is False
    assert len(calls) == 1
    failed_calls = []
    response, fallback = parse_structured_response("bad", repair=lambda *_: failed_calls.append(1) or "still bad")
    assert fallback and len(failed_calls) == 1 and response.summary


def test_schema_forbids_unknown_fields():
    payload = valid_payload(); payload["secret"] = True
    with pytest.raises(ValidationError): StructuredAnalysis.model_validate(payload)


def test_runtime_contains_three_few_shots_and_controlled_tool_example():
    assert all(f"FEW-SHOT {number}" in RUNTIME_SYSTEM_PROMPT for number in range(1, 4))
    third = RUNTIME_SYSTEM_PROMPT.split("FEW-SHOT 3", 1)[1]
    assert "solicitar tool" in third and "Resultado da tool" in third and "Nunca fabrique" in third


class Transport:
    def send(self, provider, payload, *, timeout): return {}


@pytest.mark.parametrize("provider", ["openai_responses", "anthropic_messages", "google_gemini", "xai_grok"])
def test_runtime_prompt_is_serialized_by_all_four_adapters(provider):
    adapter = ProviderToolAdapter(provider, "test", FinOpsConfig(provider=provider), Transport())
    payload = adapter._payload([{"role": "system", "content": RUNTIME_SYSTEM_PROMPT}, {"role": "user", "content": "x"}], [])
    assert "FEW-SHOT 3" in json.dumps(payload, ensure_ascii=False)
