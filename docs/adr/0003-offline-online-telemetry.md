# ADR-0003: Central offline/online mode and latency telemetry

- **Status:** Accepted
- **Date:** 2026-07-28

## Context
External APIs must be mockable, secrets must stay outside source control, and slow evidence collection needs diagnosis.

## Decision
Read runtime controls from `E3I_*` environment variables into immutable `IntelligenceConfig`. Default to offline. Track per-tool and total monotonic latency and flag budget breaches. Provider credentials remain in the existing provider-specific environment variables.

## Consequences
CI is deterministic and safe by default. Online validation is opt-in and requires injected adapters plus credentials. Latency is process-observed duration, not vendor-reported duration.
