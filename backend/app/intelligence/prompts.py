"""Grounded dossier prompt and conservative JSON repair utilities."""
from __future__ import annotations

import json
import re
from typing import Any

SYSTEM_GROUNDING_PROMPT = """You are E3I, a tactical football intelligence analyst.
Use only evidence in TOOL_EVIDENCE. Separate observations from inferences. Never invent a player,
score, formation, or event. Every conclusion must cite evidence_ids. Represent unavailable facts as
{\"value\": null, \"status\": \"missing\", \"reason\": \"...\"}. Return one valid JSON object only."""

FEW_SHOT_CASES = (
    {"input": {"evidence": [{"id": "v1", "event": "wide occupation"}]}, "output": {"observation": "wide occupation", "evidence_ids": ["v1"], "confidence": "medium"}},
    {"input": {"evidence": []}, "output": {"formation": {"value": None, "status": "missing", "reason": "no video evidence"}, "evidence_ids": [], "confidence": "low"}},
    {"input": {"evidence": [{"id": "o1", "jersey_number": "8", "quality": "blurred"}]}, "output": {"player": {"value": None, "status": "missing", "reason": "number does not establish identity"}, "evidence_ids": ["o1"], "confidence": "low"}},
)


def build_grounded_prompt(evidence: dict[str, Any]) -> str:
    examples = "\n".join(json.dumps(case, ensure_ascii=False) for case in FEW_SHOT_CASES)
    return f"{SYSTEM_GROUNDING_PROMPT}\nFEW_SHOT_CASES:\n{examples}\nTOOL_EVIDENCE:\n{json.dumps(evidence, ensure_ascii=False)}"


def repair_json_object(text: str) -> dict[str, Any]:
    """Repair common transport wrappers, never synthesize missing semantic fields."""
    candidate = text.strip().lstrip("\ufeff")
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1)
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        starts = [index for index, char in enumerate(candidate) if char == "{"]
        for start in starts:
            try:
                value, _ = decoder.raw_decode(candidate[start:])
                break
            except json.JSONDecodeError:
                continue
        else:
            raise ValueError("LLM response does not contain a valid JSON object")
    if not isinstance(value, dict):
        raise ValueError("LLM response must be a JSON object")
    return value
