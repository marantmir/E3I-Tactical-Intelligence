# Codex context

## Repository

E3I Tactical Intelligence combines a FastAPI backend in `backend/app`, pytest tests in `backend/tests`, and a React/Vite frontend in `frontend`.

## Reproducible workflow

Use Python 3.12 and Node.js 22. From the repository root, `make install` installs locked backend and frontend dependencies. `make validate` runs backend tests, Python compilation/static syntax validation, the frontend baseline test, the production build, and dependency-free lint checks.

Tests must remain offline and deterministic. The autouse fixtures isolate SQLite, copied JSON data, LLM configuration, rate limiters, and disable the LLM API key.

## Scope boundary

This baseline changes validation infrastructure only. It does not add provider tool calling, tools, paid calls, or product behavior.

## Native tool orchestration core

`backend/app/llm_tool_orchestrator.py` owns a provider-neutral, dependency-free loop. It receives normalized provider turns, limits the loop to 4 iterations by default (configurable from 1 through 8), executes only allowlisted `ToolRegistry` entries, correlates results by call ID, preserves caller history, and returns a deterministic fallback when the model fails or never completes. Tool definitions still own validation, timeout, and byte limits.

This phase proves only `get_llm_status` with mock adapters. Do not describe the four production providers as native-tool-enabled yet; their adapters and the broader tactical tool catalog are follow-up work. Existing text and multimodal paths remain separate and unchanged.
