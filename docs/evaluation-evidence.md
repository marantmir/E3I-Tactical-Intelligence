# Evidências finais de avaliação

## Identidade e escopo

- **Data:** 2026-08-02 (UTC).
- **Branch:** `fix/final-evaluation-compliance`.
- **HEAD auditado antes do commit de entrega:** `31358e2`.
- **Ambiente:** Python 3.12.13 e Node.js 20.20.2.
- **Política:** execução a partir da raiz, sem credenciais, APIs pagas ou tráfego
  de provedores. Somente documentação e artefatos determinísticos foram alterados
  depois da auditoria.

## Histórico das correções

Os merges existentes foram preservados; não houve squash, rebase ou force push.

| Etapa | Commit | Arquivos principais | Requisito atendido |
|---|---|---|---|
| Baseline | `8132e04` | `Makefile`, `pyproject.toml`, CI, testes | Quality gate reproduzível na raiz. |
| Orquestração | `9a6160a` | `llm_tool_orchestrator.py`, testes | Ciclo modelo→tool→modelo e casos negativos. |
| Tools táticas | `5974b64`, `8649e34` | `tactical_tools.py`, `tool_registry.py`, testes/evidência | Seis tools registradas e validadas. |
| Vídeo público | `b3ae46e`, `881f9aa` | rotas, YouTube e frontend | Análise de URL e fluxo de streaming. |
| Download/filtragem | `55fa93e`, `0b34200` | `youtube_video.py`, `youtube_search.py`, testes | Formato seguro e fontes previamente filtradas. |
| Multiprovedor | `f675635` | `provider_tool_adapters.py`, `llm_config.py`, testes | Quatro adaptadores, retries e fallbacks mockados. |
| Prompt/schema | `9237f3b`, `4c7ca99` | `structured_llm.py`, `llm_assistant.py`, testes | Três few-shots e resposta grounded estruturada. |
| Experimentos | `b429779` | `experiments/`, testes e docs | Pacote offline determinístico em três formatos. |
| Hardening | `13103b7` | `safe_http.py`, `check_repo.py`, CI e docs | SSRF, secrets, links e auditorias. |

## Comandos e resultados reais desta execução

| Comando | Resultado | Duração observada |
|---|---|---:|
| `python -m pytest -q` | Não concluiu: 4 erros de coleta; `httpx` ausente no Python ativo | 6 s |
| `python -m compileall -q backend/app` | Aprovado, sem saída | <1 s |
| `npm --prefix frontend run build` | Aprovado; 1.629 módulos transformados, build Vite em 5,48 s | 7 s total |
| `RUN_ONLINE_LLM_EXPERIMENTS=false python experiments/runners/run_offline.py` | Aprovado; 20 casos e JSON/CSV/Markdown regenerados | 1 s |
| `PYTHONPATH=/root/.local/share/pipx/venvs/poetry/lib/python3.12/site-packages make validate` | Aprovado na repetição final: 535 pytest em 162,94 s; 1 teste frontend; compileall, build, lints, segurança e auditorias | 184 s |
| `python scripts/lint.py` / `npm --prefix frontend run lint` | Aprovados dentro do gate: 87 Python e 90 textos; 43 arquivos frontend | incluída |
| `python scripts/check_repo.py secrets` / `sensitive` / `links` | Aprovados dentro do gate | incluída |
| `python -m pip check` | Aprovado: nenhuma dependência quebrada | incluída |
| `npm --prefix frontend audit --offline --audit-level=high` | Aprovado: 0 vulnerabilidades conhecidas no cache/lockfile | incluída |
| `git log --oneline --decorate --graph --all`; `git status`; `git remote -v` | Histórico íntegro; árvore inicialmente limpa; nenhum remote configurado | <1 s |

O `PYTHONPATH` apenas tornou visível o `httpx` 0.28.1 já instalado no ambiente
local do Poetry. Nenhum pacote foi copiado ou instalado, e nenhuma rede foi usada.
O type checking disponível neste projeto é limitado a parsing AST, compilação e
testes de schemas; não há configuração de mypy/pyright estrito.

## Cobertura objetiva da auditoria

Os 535 testes incluem o ciclo completo modelo→tool→modelo, duas tools
sequenciais, limite de iterações, tool inexistente, argumentos inválidos,
timeout, fallback entre provedores mockados, fallback determinístico local, seis
tools táticas, quatro adaptadores, três few-shots e schema de resposta. Os testes
de HTTP externo usam mocks e cobrem DNS privado e redirects. O health check
`/api/health` é exercitado localmente pela suíte FastAPI.

## Experimentos e build

O runner concluiu 20 casos fixos e atualizou `experiments/results/latest.json`,
`latest.csv` e `latest.md`. A execução recusou modo online. O build de produção
gerou os chunks Vite esperados a partir de 1.629 módulos. Experimentos online e
comparação de custo/latência de provedores reais não foram executados.

## Segurança e limitações

- Scanner de conteúdo e nomes sensíveis: aprovado; não foram encontrados segredos
  conhecidos versionados.
- Guard de rede pública e testes herméticos: cobertos no gate.
- Auditoria npm foi offline; `pip check` verifica consistência, não uma base de
  CVEs. Portanto, não se alega ausência absoluta de vulnerabilidades.
- O comando pytest literal continua dependente da instalação das dependências de
  desenvolvimento. O comando oficial é `make install` antes do gate em ambiente
  novo.
- Não foram validados deploy, console do navegador publicado, firewall de egress,
  armazenamento multi-instância nem provedores reais.

## Git, push e entrega

`git remote -v` não produziu saída e `git remote get-url origin` retornou
`error: No such remote 'origin'`. Assim, o push não pode ser alegado. Depois de
configurar o remote, o comando necessário é:

```bash
git push -u origin fix/final-evaluation-compliance
```

O GitHub CLI também não está instalado (`gh: command not found`), portanto o PR
real não é verificável neste ambiente. O corpo preparado está em
`docs/pull-request-summary.md`. Status da apresentação: pendente de gravação e
validação humana.
