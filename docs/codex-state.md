# Estado do Codex

## Fase atual

- Prompt 1 concluído: núcleo seguro e independente de provedor para tools.
- `ToolRegistry` aplica allowlist, schema/validação, timeout, limites de entrada e saída, erros sanitizados e logs sem argumentos.
- Tool registrada nesta fase: `get_llm_status`, adaptador fino do serviço de status LLM existente.
- Próxima fase: expor somente os serviços táticos existentes como tools.

## Validação

- Testes unitários isolados em `backend/tests/test_tool_registry.py`, sem chamadas externas.
