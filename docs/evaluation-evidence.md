# Evidências de avaliação

## Núcleo nativo de tool calling — 2026-08-01 (UTC)

- **Branch:** `fix/final-evaluation-compliance`
- **Pré-condição:** `8132e04 chore: establish reproducible validation baseline` confirmado no histórico antes das alterações.
- **Escopo:** orquestrador neutro de provedor e prova offline somente com `get_llm_status`; nenhum provedor pago foi chamado.

### Resultados produzidos nesta execução

| Comando | Resultado |
|---|---|
| `python -m pytest -q backend/tests/test_llm_tool_orchestrator.py` | **15 aprovados em 0,50 s** |
| `python -m pytest -q` | interrompido na coleta: 4 módulos requerem `httpx`, ausente no ambiente |
| `python -m compileall -q backend/app` | aprovado, sem saída |
| `npm --prefix frontend run build` | aprovado; 1.629 módulos transformados em 5,81 s |
| `make validate` | interrompido na etapa pytest pela mesma ausência de `httpx` |
| `python -m pip install -r backend/requirements-dev.txt` | não concluído: índice bloqueado pelo proxy (HTTP 403) |

O teste isolado cobre o fluxo usuário → modelo mock → tool → resultado → mesmo modelo mock → resposta final, além de allowlist, validação, timeout, sequência, histórico, limite de loop/bytes, sanitização, ausência de credencial, logging mínimo e fallback. A suíte completa não é declarada aprovada: a limitação ambiental acima ocorreu antes da execução dos testes não isolados. O build e a compilação obrigatórios foram executados separadamente com sucesso.

## Baseline reproduzível — 2026-08-01 (UTC)

- **Branch:** `fix/final-evaluation-compliance`
- **Commit inicial:** `cfdc2b7` (`Merge pull request #23 from marantmir/codex/corrige-esse-erro`)
- **Ambiente:** Python 3.12.13; Node.js disponível no ambiente; execução a partir da raiz do repositório.

### Diagnóstico

O primeiro `python -m pytest -q` interrompeu a coleta com quatro erros porque `httpx` não estava instalado no ambiente, embora já estivesse declarado em `backend/requirements-dev.txt`. A configuração `backend/pytest.ini` só era descoberta ao executar dentro de `backend`, e `backend/tests/conftest.py` compensava isso alterando `sys.path`. Depois da instalação, a suíte revelou um teste de rota desatualizado: ele simulava o scraper HTML, mas links do YouTube passaram a usar oEmbed, causando uma tentativa de rede e uma asserção incorreta. O frontend tinha apenas `dev`, `build` e `preview`, sem teste ou lint. Não existia workflow de CI nem comando único de validação.

### Correções

- Centralização de descoberta e imports do pytest no `pyproject.toml` raiz, eliminando a alteração manual de `sys.path`.
- Atualização do mock do teste de coleta do YouTube para a fronteira oEmbed realmente usada, mantendo a suíte offline.
- Makefile com instalação e validação completas; teste baseline e lint do frontend; lint Python/texto sem dependências adicionais.
- CI com caches nativos de pip/npm, testes, compilação, build e lint.
- Documentação dos comandos oficiais e do contexto de execução.

### Comandos e resultados reais

| Comando | Resultado | Duração observada |
|---|---|---:|
| `python -m pytest -q` (diagnóstico inicial) | 4 erros de coleta por ausência de `httpx` | 6,15 s |
| `python -m pip install -r backend/requirements-dev.txt` | não concluído: índice Python bloqueado pelo proxy (HTTP 403) | não registrada |
| `python -m pytest --collect-only -q` | 405 testes coletados | 1,07 s |
| `python -m pytest -q` (após correções) | **405 aprovados** | 65,27 s |
| `python -m compileall -q backend/app` | aprovado, sem saída | < 1 s |
| `npm --prefix frontend install` | aprovado, dependências já sincronizadas | 0,65 s |
| `npm --prefix frontend test` | **1 aprovado** | 0,21 s |
| `npm --prefix frontend run build` | aprovado; 1.629 módulos transformados | 5,16 s |
| `python scripts/lint.py` | aprovado; 74 arquivos Python e 76 arquivos de texto verificados | < 1 s |
| `npm --prefix frontend run lint` | aprovado; 43 arquivos verificados | < 1 s |
| `git diff --check` | aprovado | < 1 s |

### Limitações restantes

O proxy deste ambiente rejeitou acesso ao índice Python, então a instalação pip completa não pôde ser repetida aqui. Para validar a suíte, `httpx` 0.28.1 foi disponibilizado a partir de outro ambiente Python já instalado no mesmo contêiner; nenhuma cópia foi adicionada ao repositório. Em CI ou em uma máquina com acesso ao índice, `python -m pip install -r backend/requirements-dev.txt` é o caminho oficial e instalará a versão fixada. O aviso npm sobre a configuração legada `http-proxy` pertence ao ambiente e não afetou instalação, testes ou build.

O frontend ainda não possui testes de componentes ou navegador; o teste adicionado estabelece apenas o contrato mínimo reproduzível do projeto. A verificação estática Python é deliberadamente mínima (parse AST + `compileall`) porque o código existente não possui anotações suficientes para introduzir um type checker estrito sem uma migração fora do escopo.
