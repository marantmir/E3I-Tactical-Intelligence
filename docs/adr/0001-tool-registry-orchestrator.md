# ADR-0001: Registry and fail-soft orchestrator

- **Status:** Accepted
- **Date:** 2026-07-28

## Context
Search, OCR, video, and metrics have different availability and failure modes. Direct calls couple the dossier pipeline to vendors and make offline tests difficult.

## Decision
Use a typed `ToolRegistry`, dependency-injected adapters, and a `ToolOrchestrator`. Online tools are gated in offline mode. Every tool boundary records status and latency; failures become explicit `DADO_AUSENTE` annotations and do not abort other tools.

## Consequences
Tool implementations can be mocked without network access and independently replaced. Callers must inspect missing-data annotations rather than assume every requested output exists. Parallel execution is deliberately deferred; the central concurrency parameter reserves that evolution without introducing nondeterministic traces now.
