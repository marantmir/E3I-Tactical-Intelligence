# Structured Delivery Report

## Executive Summary
The delivery adds an extensible tool runtime, evidence-grounded LLM contract, conservative JSON repair, centralized offline/online controls, and latency-aware reflective traces. External behavior is mockable and offline-safe; unavailable evidence is annotated rather than inferred.

## Commit Table
| Phase | Scope | Artifact |
|---|---|---|
| Diagnosis | Coupling, partial-data, prompt-output risks | ADR context and audit matrix |
| Implementation | Registry, orchestrator, adapters, config, prompt repair | `backend/app/intelligence/` |
| Tests | Mock tools, modes, resilience, prompt/repair | `test_intelligence_runtime.py` |
| Docs | ADRs, Mermaid, lessons, talk track | `docs/` and README |
| Validation | Full Python suite and frontend build | commands recorded below |

## Tool Implementation
| Tool | Boundary | Online required | Missing-data behavior |
|---|---|---:|---|
| Search | injected callable | Yes | skipped offline and annotated |
| OCR | injected callable | No | error isolated and annotated |
| Video | injected callable | No | error isolated and annotated |
| Metrics | injected callable | No | error isolated and annotated |

## Parameters
| Environment variable | Default | Constraint |
|---|---:|---|
| `E3I_INTELLIGENCE_MODE` | `offline` | `offline` / `online` |
| `E3I_TOOL_TIMEOUT_SECONDS` | `12` | 0.1–90 seconds |
| `E3I_MAX_PARALLEL_TOOLS` | `4` | 1–16 (reserved) |
| `E3I_LATENCY_BUDGET_MS` | `20000` | 100–120000 ms |
| `E3I_ANNOTATE_MISSING_DATA` | `true` | boolean |

## Results
The mock suite verifies deterministic offline gating and online fail-soft behavior without credentials. Latency uses a monotonic clock. The LLM boundary accepts valid objects behind common transport noise and rejects invalid/non-object output.

## ADR Index
1. [ADR-0001 — Tool registry and orchestrator](adr/0001-tool-registry-orchestrator.md)
2. [ADR-0002 — Grounded JSON contract](adr/0002-grounded-json-contract.md)
3. [ADR-0003 — Offline/online telemetry](adr/0003-offline-online-telemetry.md)

## Validation Logs
Commands and final outcomes are recorded in the delivery response. External APIs remain mocked; a live-provider smoke test is intentionally excluded because it would require secrets and incur vendor/network variability.

## Audit Matrix
| Requirement | Implementation | Evidence |
|---|---|---|
| Registry/orchestrator | typed definitions and fail-soft runner | unit tests and ADR-0001 |
| Search/OCR/Video/Metrics | injected default catalog | catalog test |
| Grounding + 3 examples | common prompt constant | prompt contract test |
| JSON repair | conservative object decoder | parameterized tests |
| Central parameters | immutable environment config | clamp/mode test |
| Offline/online | online gate, mocked execution | two mode tests |
| Latency | per-tool/total monotonic fields | trace assertions |
| Missing data | `DADO_AUSENTE` annotation | offline/error tests |
| Docs/presentation | ADRs, Mermaid, lessons, six-minute script | documentation files |
| Secrets | environment-only provider credentials | existing config + ADR-0003 |
