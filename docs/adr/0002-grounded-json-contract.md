# ADR-0002: Grounded JSON output contract

- **Status:** Accepted
- **Date:** 2026-07-28

## Context
Provider output can contain Markdown fences or prose, while tactical hallucinations create operational risk.

## Decision
Apply one system grounding contract, exactly three few-shot cases (positive evidence, absent formation evidence, ambiguous OCR), and conservative JSON repair. Repair removes transport wrappers and extracts a valid object; it never manufactures semantic fields. Invalid payloads trigger the existing deterministic fallback.

## Consequences
Provider behavior is consistent and auditable. Schema validation remains a future strengthening; callers must continue merging domain defaults deliberately.
