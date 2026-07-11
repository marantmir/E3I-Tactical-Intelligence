# Registro do Agente

## Entrega - Amostragem de video completo na visao computacional (11/07/2026)

Correcao no pipeline de visao computacional (`backend/app/video_vision.py`): antes, `process_video` lia o video sequencialmente a partir do inicio e parava ao atingir `max_frames`, entao um video longo (ex.: 30s+) so tinha analisados os primeiros segundos. Agora:

- Ao abrir o video, le `CAP_PROP_FRAME_COUNT` para descobrir a duracao total em frames.
- Quando a duracao e conhecida, calcula um `sample_every` que distribui as amostras (via seek com `CAP_PROP_POS_FRAMES`, sem decodificar os frames pulados) do primeiro ao ultimo frame do arquivo, entao o heatmap, o grafo, os rastros e o video anotado passam a representar a partida inteira, nao so o inicio.
- Quando a duracao nao pode ser determinada (codec/container sem contagem confiavel), mantem o comportamento antigo (sequencial a partir do inicio) como fallback seguro.
- `processing_config` agora expoe `source_total_frames`, `requested_sample_every`, `sample_every` (efetivo) e `full_video_coverage`; o frontend (`VideoVisionPanel.jsx`) exibe um aviso confirmando a amostragem distribuida no video completo.
- Testes novos cobrindo cobertura total (video sintetico longo com `max_frames` pequeno) e o fallback sequencial.

## Entrega - Fase 2 do roadmap: resiliencia sem login (11/07/2026)

Continuacao do roadmap de auditoria, restrita aos itens que nao dependem da decisao de produto sobre login/admin de usuarios:

- Rate limiting em memoria (`backend/app/rate_limit.py`, sem dependencia nova) aplicado as rotas de upload de video (`/api/teams/{team_id}/video-vision/upload` e `/api/teams/video-vision/upload`), configuravel via `VIDEO_UPLOAD_RATE_LIMIT`/`VIDEO_UPLOAD_RATE_WINDOW_SECONDS`. Retorna 429 com `Retry-After` quando excedido.
- Logging estruturado em JSON (`backend/app/logging_config.py`) com correlacao por `request_id` (middleware em `main.py`, cabecalho `X-Request-ID` na resposta), substituindo a ausencia de logs por linhas JSON parseaveis por qualquer agregador.
- Testes novos: `test_rate_limit.py`, `test_logging_config.py`, e casos adicionais em `test_routes_teams.py` (429 no upload, presenca do `X-Request-ID`).

Login/admin de usuarios e a consolidacao com um segundo backend continuam fora de escopo (decisao de produto pendente).

## Entrega - Ajustes de auditoria (11/07/2026)

Aplicados os itens de um plano de auditoria tecnica que tem correspondencia direta neste repositorio (FastAPI + React, sem `server.ts`/autenticacao, que existem apenas numa versao paralela do projeto):

- CORS do FastAPI restrito por `ALLOWED_ORIGINS` (env, default `localhost:5173`) em vez de `allow_origins=["*"]`.
- Code-splitting por rota no frontend (`React.lazy` + `Suspense` em `App.jsx`), reduzindo o bundle inicial.
- Suite `pytest` em `backend/tests/`: `graph_analysis.py`, `video_vision.py` (video sintetico gerado no proprio teste) e rotas criticas de `teams`/`analysis` (incluindo upload de video e criacao/consulta de historico), com banco SQLite isolado por teste e chamadas de rede/LLM mockadas.

Itens que dependem de decisao de produto (login/admin de usuarios, consolidacao arquitetural com um segundo backend) foram deixados de fora por nao existirem hoje neste repositorio.

## Entrega Anterior

O agente evoluiu o E3I Tactical Intelligence para uma plataforma de inteligencia tatica com:

- Busca publica e local sobre o time analisado.
- Pre-analise antes do salvamento.
- Endpoints de grafo tatico, leitura visual de videos e inteligencia publica.
- Painel visual de grafo em `Formacoes`.
- Painel de visao computacional em `Fontes, videos e leitura visual`.
- Relatorio final consolidado.
- Documentacao atualizada para a nova arquitetura.

## Decisoes Tecnicas

- Manter FastAPI e React/Vite.
- Evitar novas dependencias para preservar portabilidade.
- Usar Wikimedia como fonte publica aberta quando a rede permitir.
- Manter modo local quando a rede externa estiver indisponivel.
- Separar busca publica, grafo, video e persistencia em modulos independentes.

## Validacoes

- Testes HTTP com `TestClient`.
- Build de frontend com `npm run build`.
- Verificacao visual no navegador local.
- Varredura de textos antigos no codigo e nos dados exibidos.
