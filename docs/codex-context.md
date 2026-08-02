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

The registry now also exposes six validated tactical adapters over existing search, visual analysis, graph, operational-research, and local-data services. Each returns explicit provenance/nature/limitations. Mock orchestration proves one and two sequential tactical calls. Do not describe the four production providers as native-tool-enabled yet: their wire adapters remain follow-up work.

## Estado: adapters de tool calling

Há codecs mockáveis para OpenAI Responses, Anthropic Messages, Google Gemini e xAI Grok, matriz central em `PROVIDER_CAPABILITIES`, limites em `FinOpsConfig` e fallback remoto opt-in. Não usar credenciais reais em testes. Validação online dos provedores: não executada.

## Estado: prompting e schema runtime

`structured_llm.py` é a fonte real do contrato comum e dos três few-shots. O schema rejeita extras, incoerência de confiança, referências órfãs e certeza sem evidência. O reparo é opcional e ocorre uma vez; falha termina em resposta válida de confiança zero. Nunca registrar prompt do usuário, conteúdo de tool ou segredo nos documentos/evidências.
Os exemplos runtime permanecem compactos, mas agora incluem todos os campos obrigatórios; fences Markdown com texto externo são inválidas.
