# Codex context

## Repository

E3I Tactical Intelligence combines a FastAPI backend in `backend/app`, pytest tests in `backend/tests`, and a React/Vite frontend in `frontend`.

## Reproducible workflow

Use Python 3.12 and Node.js 22. From the repository root, `make install` installs locked backend and frontend dependencies. `make validate` runs backend tests, Python compilation/static syntax validation, the frontend baseline test, the production build, and dependency-free lint checks.

Tests must remain offline and deterministic. The autouse fixtures isolate SQLite, copied JSON data, LLM configuration, rate limiters, and disable the LLM API key.

## Scope boundary

This baseline changes validation infrastructure only. It does not add provider tool calling, tools, paid calls, or product behavior.
