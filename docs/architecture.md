# Arquitetura

## Visao Geral

O E3I Tactical Intelligence e uma aplicacao full stack com frontend React, backend FastAPI e persistencia local em SQLite.

```text
Usuario
  -> Frontend React/Vite
  -> Cliente HTTP
  -> Backend FastAPI
  -> Busca publica Wikimedia
  -> Data store JSON local
  -> Modulo de grafos taticos
  -> Modulo de leitura visual de videos
  -> SQLite para historico
```

## Backend

Arquivos principais em `backend/app`:

- `main.py`: inicializa FastAPI, CORS, rotas e frontend buildado.
- `database.py`: cria e consulta historico em SQLite.
- `data_store.py`: carrega dados locais em JSON.
- `online_search.py`: busca publica e fallback de modo local.
- `graph_analysis.py`: monta nos, arestas, metricas e insights de rede.
- `video_vision.py`: monta mapa de calor, trilhas, frames e eventos de video.
- `routes/teams.py`: endpoints de times, fontes, grafo, video e inteligencia publica.
- `routes/analysis.py`: pre-analise, criacao de analise e historico.
- `routes/reports.py`: relatorio final consolidado.

## Frontend

Principais telas:

- Dashboard
- Nova analise
- Busca de time
- Dossie tatico
- Formacoes com grafo visual
- Elenco
- Fontes, videos e leitura visual
- Plano de jogo
- Relatorio final
- Historico
- Inteligencia avancada

## Dados e Evidencias

Os dados locais ficam em `backend/data`. Eles sustentam a experiencia quando uma API externa nao esta disponivel e sao combinados com busca publica na pre-analise.

A busca publica retorna fontes quando a rede permite. Quando a consulta externa falha, o backend retorna `local_fallback` com uma fonte publica sugerida e mantem o fluxo de analise ativo.

## Deploy

O `Dockerfile` cria o build React e serve os arquivos estaticos pelo FastAPI. Assim, um unico endpoint publico abre a interface e responde as rotas `/api`.

## Extensoes

As proximas evolucoes naturais sao:

- Upload de video e extracao real de tracking.
- Integracao com APIs esportivas premium.
- Otimizacao numerica para formacao, estrategia e substituicoes.
- Relatorios exportados em PDF com evidencias anexadas.

## Orquestracao nativa de tools (nucleo)

`llm_tool_orchestrator.py` separa o formato de cada provedor (`ProviderToolAdapter`) do loop seguro. Uma resposta normalizada pode encerrar com texto ou solicitar `NormalizedToolCall`; o orquestrador normaliza JSON, encaminha exclusivamente ao `ToolRegistry`, correlaciona `NormalizedToolResult` por `tool_call_id`, anexa ambos ao histórico e chama o mesmo adaptador novamente.

O limite padrão é 4 iterações e a configuração aceita somente 1 a 8. Cada definição do registry conserva timeout e limites próprios de entrada/saída; o orquestrador também limita argumentos antes da validação. Tools desconhecidas nunca são resolvidas dinamicamente. Erros internos são convertidos em mensagens genéricas; logs contêm apenas provedor, nome, status e duração, sem payload integral.

A allowlist registra `get_llm_status` e seis tools táticas. `tactical_tools.py` contém somente schemas, delegação e envelope de proveniência; busca/ranking, visão, grafo, otimização e dados continuam nos serviços de domínio. O catálogo e a matriz serviço/input/output/natureza estão em `docs/tool-catalog.md`. Os formatos nativos de tool calling dos quatro provedores **ainda não estão integrados**; o fluxo integrado usa adaptador mockado hermético.

## Fronteira multiprovedor de tools

`provider_tool_adapters.py` separa quatro codecs de wire format do `LLMToolOrchestrator`. O orquestrador mantém allowlist, validação e limites; adaptadores filtram parâmetros pela matriz central, fazem retry transitório e normalizam respostas. `FallbackProviderAdapter` seleciona apenas provedores configurados, preserva o histórico normalizado, registra a rota e encerra no fallback determinístico.

## Respostas semânticas estruturadas

`structured_llm.py` concentra prompt runtime, modelos Pydantic fechados e pipeline parse → extração Markdown controlada → validação → um reparo opcional → fallback estruturado. Referências de findings/recomendações precisam apontar para evidências existentes; confiança deve concordar com sua faixa; evidência vazia não pode sustentar certeza. `_system_with_preferences` injeta o contrato comum junto da instrução específica em todos os quatro caminhos HTTP de provedor, preservando os formatos consumidos pelo frontend existente.
Conflitos multimodais declarados formam uma invariável adicional: devem conter fontes `image` e `metric` e manter score abaixo de `0.4`.
