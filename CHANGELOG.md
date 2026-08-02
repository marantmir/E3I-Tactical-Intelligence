# Changelog

## Unreleased

### Changed

- Centralized root-level pytest discovery and backend import configuration.
- Added reproducible Make targets, backend/frontend checks, and a complete GitHub Actions CI workflow.
- Added a frontend baseline test and dependency-free lint checks.
- Documented setup, validation, evidence, and remaining environment limitations.

### Added

- Added a deterministic 20-case offline evaluation package with synthetic text, metrics, frames and tools; documented metrics; JSON/CSV/Markdown reports; output schema; and hermetic reproducibility/network-isolation tests.

- Added a provider-neutral native tool-calling orchestrator with normalized calls/results, correlated history, a bounded model loop, safe registry execution, sanitized failures, and deterministic fallback.
- Added an offline end-to-end mock-provider test suite proving the initial `get_llm_status` flow and its safety limits.
- Added six allowlisted tactical tools with strict Pydantic inputs, bounded execution, sanitized serializable outputs, explicit provenance, a service catalog, and hermetic unit/orchestrator tests.
- Added a grounded runtime system prompt with three compact few-shots, strict nested response schemas, controlled JSON/Markdown parsing, one optional repair, and a structured insufficient-evidence fallback.
- Hardened structured LLM validation with schema-valid runtime examples, whole-response Markdown extraction, and low-confidence image/metric conflict semantics.

## Unreleased — provider tool adapters

- Added capability-aware OpenAI, Anthropic, Gemini and Grok tool adapters.
- Added bounded transient retries, credential-aware configurable provider fallback and deterministic local fallback.
- Centralized FinOps limits and added hermetic provider contract tests.

## 2026-08-02 — hardening e documentação as-built

- Adicionada política de saída HTTPS com validação DNS, bloqueio de redes não públicas e redirects limitados/revalidados.
- Consolidado controle de tools, limites, timeout, erros sanitizados e logs sem payloads.
- Adicionados scanner de segredos, verificação de arquivos sensíveis/links e auditoria de dependências ao quality gate e CI.
- Criados `.env.example` e ADR sobre APIs diretas; arquitetura, README e documentação transversal alinhados ao código atual.
