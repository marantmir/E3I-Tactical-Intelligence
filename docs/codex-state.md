# Estado do trabalho Codex

## Fase atual

Prompt 0 concluído: contexto compacto e memória persistente preparados, sem alteração funcional.

## Ponto inicial

- Branch: `work`.
- Commit inicial: `bf08de33106394c24f097ff1872b3fd0257f4e00`.
- Alterações locais encontradas no início: nenhuma.

## Alterações desta fase

- Criados `AGENTS.md`, `docs/codex-context.md` e este arquivo.
- Substituído `docs/evaluation-checklist.md` pelo formato de avaliação solicitado.

## Próximos passos

Escolher uma única lacuna do checklist, confirmar seu escopo e implementar/testar em commit isolado. Não reanalisar o repositório inteiro; partir de `docs/codex-context.md` e fazer apenas buscas direcionadas.

## Arquivos relevantes

`backend/app/llm_assistant.py`, `llm_config.py`, `video_vision.py`, `operational_research.py`, `tactical_search/`, `backend/tests/`, `frontend/package.json`, `README.md` e `docs/architecture.md`.

## Testes disponíveis

- Backend: `cd backend && pytest` (suíte completa não executada nesta fase).
- Frontend: `cd frontend && npm run build`.
- Lint e type checking: não configurados.

## Riscos conhecidos

Busca e LLM podem acessar rede; devem ser mockados em testes. A configuração LLM pode conter segredo local. Visão computacional é CPU-intensiva e heurística. Documentação de arquitetura tem trechos defasados. Não há gates estáticos de lint/tipos.

