# Changelog

## Unreleased

### Changed

- Centralized root-level pytest discovery and backend import configuration.
- Added reproducible Make targets, backend/frontend checks, and a complete GitHub Actions CI workflow.
- Added a frontend baseline test and dependency-free lint checks.
- Documented setup, validation, evidence, and remaining environment limitations.

### Added

- Added a provider-neutral native tool-calling orchestrator with normalized calls/results, correlated history, a bounded model loop, safe registry execution, sanitized failures, and deterministic fallback.
- Added an offline end-to-end mock-provider test suite proving the initial `get_llm_status` flow and its safety limits.
- Added six allowlisted tactical tools with strict Pydantic inputs, bounded execution, sanitized serializable outputs, explicit provenance, a service catalog, and hermetic unit/orchestrator tests.

## Unreleased — provider tool adapters

- Added capability-aware OpenAI, Anthropic, Gemini and Grok tool adapters.
- Added bounded transient retries, credential-aware configurable provider fallback and deterministic local fallback.
- Centralized FinOps limits and added hermetic provider contract tests.
