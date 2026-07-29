# Six-minute technical presentation and Q&A

## 0:00–0:45 — Problem and diagnosis
Tactical evidence arrives through heterogeneous search, OCR, video, and metrics paths. Previously, provider invocation existed but there was no common execution boundary, offline contract, or uniform latency record. The risk was hidden partial data and provider-shaped coupling.

## 0:45–1:45 — Architecture
Show the README Mermaid diagram. Explain the registry as discovery, injected adapters as anti-corruption boundaries, and the orchestrator as policy: mode gating, fail-soft execution, provenance, latency, and explicit missing data. SQLite and existing FastAPI routes remain stable.

## 1:45–2:45 — LLM grounding
Walk through the evidence-only system rule and the three cases: evidenced observation, absent formation, ambiguous jersey OCR. Demonstrate fenced/prose-wrapped JSON repair. Emphasize that repair fixes syntax transport noise, never missing football facts.

## 2:45–3:35 — Parameters and security
Demonstrate `E3I_INTELLIGENCE_MODE`, timeout, concurrency ceiling, latency budget, and missing-data annotation. Offline is the default. API keys remain provider-specific environment secrets and are neither logged nor committed.

## 3:35–4:35 — Test strategy
Unit tests inject pure mocks for all four tools. Offline tests prove search cannot run; online tests prove one tool outage does not erase successful evidence. Prompt and repair tests lock the three-case contract. The existing full backend and frontend suites detect regressions.

## 4:35–5:25 — Operational traces
Each invocation emits a P-P-R-L trace: Perceive input, Plan tool sequence, Reason over grounded output, Learn from status/latency. Explain `DADO_AUSENTE` as an analyst-visible boundary rather than silent zero or fabricated value.

## 5:25–6:00 — Trade-offs and next step
Sequential execution favors reproducibility; bounded parallelism is the next measured optimization. Follow with JSON Schema validation and persistence of sanitized trace summaries in SQLite.

## Q&A

**Why not let the LLM select arbitrary tools?** The application owns the allowlisted plan; this limits cost, prompt injection, and nondeterminism.

**Does repair hide bad model output?** No. It accepts only a decodable object. Irrecoverable or semantically absent data goes to explicit fallback/missing state.

**How are vendors swapped?** Provider calls and tool handlers are injected behind stable contracts; tests never require live APIs.

**Why sequential with a parallel parameter?** Deterministic traces are the safe baseline. The parameter centralizes the future constraint, but no concurrency claim is made until measured.
