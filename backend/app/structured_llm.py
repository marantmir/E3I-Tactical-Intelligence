"""Grounded runtime prompt and strict parsing for primary LLM analyses."""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

MAX_RESPONSE_BYTES = 32_000


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Evidence(StrictModel):
    id: str = Field(min_length=1, max_length=64)
    source: Literal["text", "image", "metric", "tool"]
    description: str = Field(min_length=1, max_length=600)
    reference: str = Field(min_length=1, max_length=240)


class Finding(StrictModel):
    statement: str = Field(min_length=1, max_length=800)
    kind: Literal["fact", "inference", "hypothesis"]
    evidence_ids: list[str] = Field(min_length=1, max_length=12)


class Confidence(StrictModel):
    score: float = Field(ge=0, le=1)
    level: Literal["low", "medium", "high"]
    rationale: str = Field(min_length=1, max_length=400)

    @model_validator(mode="after")
    def level_matches_score(self) -> "Confidence":
        expected = "low" if self.score < 0.4 else "medium" if self.score < 0.75 else "high"
        if self.level != expected:
            raise ValueError("confidence level does not match score")
        return self


class Limitation(StrictModel):
    description: str = Field(min_length=1, max_length=500)
    impact: Literal["low", "medium", "high"]


class Recommendation(StrictModel):
    action: str = Field(min_length=1, max_length=500)
    priority: Literal["low", "medium", "high"]
    evidence_ids: list[str] = Field(default_factory=list, max_length=12)


class StructuredAnalysis(StrictModel):
    summary: str = Field(min_length=1, max_length=1200)
    findings: list[Finding] = Field(max_length=40)
    evidence: list[Evidence] = Field(max_length=60)
    confidence: Confidence
    limitations: list[Limitation] = Field(min_length=1, max_length=20)
    recommendations: list[Recommendation] = Field(max_length=20)

    @model_validator(mode="after")
    def evidence_is_consistent(self) -> "StructuredAnalysis":
        ids = [item.id for item in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence ids must be unique")
        referenced = {ref for finding in self.findings for ref in finding.evidence_ids}
        referenced |= {ref for item in self.recommendations for ref in item.evidence_ids}
        if referenced - set(ids):
            raise ValueError("all evidence references must exist")
        if not self.evidence and (self.findings or self.confidence.score >= 0.4):
            raise ValueError("empty evidence requires no findings and low confidence")
        return self


RUNTIME_SYSTEM_PROMPT = """PAPEL: Você é o analista tático responsável por uma resposta auditável.
GROUNDING: use somente texto, imagens, métricas e resultados de tools presentes no contexto. Nunca invente nomes, eventos, placares ou medições. Classifique cada conclusão como fact, inference ou hypothesis e associe evidence_ids.
CONFLITOS: quando imagem, texto e métricas divergirem, registre o conflito; não escolha uma versão sem suporte e reduza a confiança. Declare limitações e evidência ausente.
TOOLS: solicite apenas tools disponibilizadas, somente quando necessárias; não simule chamadas ou resultados. Após a tool, fundamente a resposta no resultado retornado.
SAÍDA: retorne somente JSON compatível com summary, findings, evidence, confidence {score 0..1, level, rationale}, limitations e recommendations. Sem evidência suficiente, use findings/evidence vazios, confiança baixa e recomende coleta verificável.

FEW-SHOT 1 — EVIDÊNCIA TEXTUAL SUFICIENTE
Entrada: texto oficial: "bloco médio aos 60 min".
Saída: {"evidence":[{"id":"e1","source":"text","description":"bloco médio aos 60 min","reference":"texto oficial"}],"findings":[{"statement":"Houve bloco médio aos 60 min","kind":"fact","evidence_ids":["e1"]}],"confidence":{"score":0.85,"level":"high","rationale":"fonte textual direta"},"limitations":[{"description":"sem vídeo para duração","impact":"medium"}]}

FEW-SHOT 2 — CONFLITO MULTIMODAL
Entrada: imagem sugere linha alta; métrica registra bloco baixo.
Saída: {"evidence":[{"id":"e1","source":"image","description":"possível linha alta","reference":"frame 12s"},{"id":"e2","source":"metric","description":"bloco baixo","reference":"shape.block"}],"findings":[{"statement":"Imagem e métrica estão em conflito; não há conclusão sobre a altura do bloco","kind":"fact","evidence_ids":["e1","e2"]}],"confidence":{"score":0.3,"level":"low","rationale":"conflito multimodal"},"limitations":[{"description":"um único frame","impact":"high"}]}

FEW-SHOT 3 — USO DE TOOL
Entrada: dados insuficientes para densidade. Ação: solicitar tool get_graph_analysis. Resultado da tool: {"density":0.42,"source":"tracking"}. Resposta final: evidence inclui source tool/reference get_graph_analysis; finding inference="densidade moderada", confidence medium; limitation="tracking heurístico". Nunca fabrique o resultado da tool.
"""


def structured_fallback(reason: str = "insufficient_or_invalid_evidence") -> StructuredAnalysis:
    return StructuredAnalysis(
        summary="Não há evidência válida suficiente para uma conclusão fundamentada.",
        findings=[], evidence=[],
        confidence=Confidence(score=0.0, level="low", rationale="Resposta inválida ou evidência insuficiente."),
        limitations=[Limitation(description=reason[:500], impact="high")],
        recommendations=[Recommendation(action="Fornecer evidência verificável e repetir a análise.", priority="high")],
    )


def _decode(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
        if len(blocks) != 1:
            raise
        return json.loads(blocks[0])


def parse_structured_response(
    text: str, *, repair: Callable[[str, str], str] | None = None
) -> tuple[StructuredAnalysis, bool]:
    """Parse/validate, optionally repair exactly once, otherwise return fallback."""
    error = "invalid_response"
    for attempt in range(2):
        try:
            if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_RESPONSE_BYTES:
                raise ValueError("response_too_large")
            return StructuredAnalysis.model_validate(_decode(text)), False
        except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as exc:
            error = str(exc)
            if attempt == 0 and repair is not None:
                text = repair(text, error)
                continue
            break
    return structured_fallback(error), True
