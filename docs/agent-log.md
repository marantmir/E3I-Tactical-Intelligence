# Registro do Agente

## Entrega - Leitura visual direta por LLM multimodal (18/07/2026)

Ate aqui, a "analise por LLM" do video (`analyze_video_tactics`, `identify_players_from_tracks`) so recebia numeros e resumos produzidos pela visao computacional (OpenCV) - o LLM nunca via de fato uma imagem do jogo, apesar do pipeline ja gerar um video anotado. O pedido era usar visao computacional de forma eficiente para viabilizar uma leitura **visual** real por LLM, entao a mudanca fecha essa lacuna sem duplicar o pipeline de CV:

- **Captura de key frames reais** (`backend/app/video_vision.py`): durante o loop principal de `process_video`, o frame anotado (com caixas/trilhas/overlay tatico) e comprimido e guardado em base64 nos poucos instantes de maior sinal ja detectados pela propria CV - abertura, mudanca de padrao tatico, disputa/desarme e conducao em alta velocidade - alem do fechamento. Limitado a 6 frames (`MAX_VISUAL_KEY_FRAMES`), redimensionados para 480px de largura e JPEG qualidade 65 (`_encode_key_frame`/`_maybe_capture_key_frame`) para manter baixo o custo/latencia de uma chamada de visao. Exposto no resultado como `visual_key_frames`.
- **Suporte multimodal nos 4 provedores** (`backend/app/llm_assistant.py`): `_call_llm_json` e os quatro `_call_*` (OpenAI Responses, Anthropic Messages, Google Gemini, xAI Grok) ganharam um parametro `images` opcional, cada um no formato nativo do provedor (`input_image` com data URI, bloco `image` base64, `inlineData`, `image_url`). Nova funcao `analyze_video_visually()` manda os key frames reais + contexto estruturado (team_focus, shape_analysis) pedindo que o LLM descreva o que efetivamente ve em cada imagem e cruze com as metricas de rastreamento, apontando concordancias/divergencias - sem API key ou sem frames capturados, cai no mesmo padrao de fallback deterministico do resto do app.
- **Rota**: `_build_video_result` (`backend/app/routes/teams.py`) agora tambem retorna `llm_visual_analysis`.
- **Frontend** (`VideoVisionPanel.jsx` + `styles.css`): nova secao "Leitura visual direta por LLM multimodal" mostra os thumbnails dos key frames reais (clicaveis, pulam para o instante no video) ao lado da observacao do LLM para cada um e do cross-check com as metricas.
- Testes novos: captura/limite de key frames em `test_video_vision.py`; formato do payload de imagem para os 4 provedores e os caminhos de fallback/enriquecido de `analyze_video_visually` em `test_llm_assistant.py`.

## Entrega - Base de dados online real (Wikipedia) + progresso ao vivo na visao computacional (11/07/2026)

Dois pedidos combinados: (1) uma base online de verdade alimentando a ferramenta, restrita a fontes gratuitas/publicas; (2) sensacao de "tempo real" no processamento de video, mantendo o modelo de upload em lote (nao streaming de camera ao vivo).

- **Wikipedia como base online real** (`backend/app/wikipedia_lookup.py`): sem chave de API, usa a REST API publica do Wikipedia (pt, com fallback en) para trazer descricao, resumo e principalmente o **escudo/imagem do time**. Wireado em `online_search.py` (campo `crest_url`/`wikipedia` no resultado de busca) e em `routes/teams.py` (`_team_crest_url`, cache via `lru_cache`) para times locais, perfis salvos e perfis de busca online.
- **Escudos visiveis na interface**: `TeamCard`, o hero do Dossie e os cards do Confronto agora mostram o escudo do time quando disponivel (`.team-crest`/`.team-crest-large` em `styles.css`) - reforca o pedido de "ferramenta mais visual".
- **Progresso ao vivo no processamento de video** (`backend/app/video_jobs.py` + rotas `POST .../video-vision/jobs` e `GET .../video-vision/jobs/{id}/events`): o upload roda em thread de segundo plano (`process_video` ganhou um callback `on_progress`) e o frontend acompanha via Server-Sent Events, atualizando uma barra de progresso real (`VideoProcessingProgress` em `VideoVisionPanel.jsx`) com frames processados e percentual, em vez de so esperar o resultado final. O endpoint sincrono anterior continua existindo (compatibilidade).
- Corrigido de brinde um bug de sobreposicao visual nos controles de frames/intervalo/equipe (`.vision-processing-controls`) percebido durante o teste do progresso ao vivo.
- Testes novos: `test_wikipedia_lookup.py`, `test_online_search.py` e casos de job/SSE em `test_routes_teams.py`.
- Nao testavel neste ambiente de desenvolvimento: a rede de sandbox bloqueia `wikipedia.org`/`duckduckgo.com` (politica de egress), entao a integracao foi validada com testes unitarios mockados; a chamada real de rede deve ser validada apos o deploy (Render tem acesso normal a internet).

## Entrega - Meu time, cadastro-ou-selecao e Confronto (11/07/2026)

Nova funcionalidade, inspirada no conceito de "own team" de uma versao paralela do projeto (zip enviado), mas reimplementada com o design system atual (sem os estilos inline daquela versao) e sem os campos que ja existem via `online-profiles`/`teams`:

- Backend: tabela `own_team_setting` (uma linha global) + `GET/PUT /api/teams/own-team`, guardando so a `ref` (reaproveita o mesmo universo de times local/online ja exposto por `team_options`/`workspace`).
- Frontend: tela nova `Meu time` (`/meu-time`) para selecionar entre times ja conhecidos ou cadastrar um novo e marca-lo como seu time ativo.
- `NewAnalysis.jsx`: ao sair do campo de nome do time, o app verifica se ele existe (base local ou perfil salvo); se existir, so seleciona; se nao existir, a acao principal passa a ser "Cadastrar time" (salva o perfil online) antes de liberar a analise.
- O nome verificado/cadastrado fica salvo (`localStorage`) e alimenta automaticamente o campo de busca em `Buscar time`.
- Tela nova `Confronto` (`/team/:teamId/matchup`) comparando o seu time ativo com o time analisado (formacao, pontos fortes/fracos, elenco). O link some e a pagina mostra aviso quando o time analisado e o proprio time ativo, ja que um time nao joga contra si mesmo.
- Testes novos para os endpoints `own-team` (default vazio, definir um ref valido, rejeitar ref invalido).

## Entrega - Sondagem robusta de duracao do video (11/07/2026)

Reforco da correcao anterior de cobertura total de video: `CAP_PROP_FRAME_COUNT` (metadado do container) pode ser 0, ausente ou errado para gravacoes de celular/webm nao finalizado, o que fazia o pipeline cair no fallback sequencial (voltando a analisar so o inicio do video) mesmo com a correcao de amostragem ja aplicada. Agora `video_vision.py` sonda a duracao real diretamente no decodificador via busca exponencial + binaria (`_probe_total_frames`, seek com `CAP_PROP_POS_FRAMES` + `read()`), corrigindo tanto metadados subestimados quanto ausentes, e so cai no fallback sequencial quando o arquivo realmente nao suporta seek (caso raro). Testes cobrem: metadado zerado, metadado subestimado e capture sem suporte a seek.

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
