# Contexto compacto do repositório

## Stack real

- Backend: Python, FastAPI, Uvicorn, Pydantic, SQLite, pytest/httpx.
- Frontend: React 19, React Router, Vite 6 e JavaScript/JSX (sem TypeScript).
- Análise: OpenCV headless e NetworkX. Deploy: Docker/Render; o FastAPI serve `frontend/dist`.

## Estrutura principal

- `backend/app/main.py` inicializa API, CORS, rotas e arquivos estáticos.
- `backend/app/routes/` contém endpoints; `database.py` persiste histórico em SQLite; `data_store.py` e `backend/data/*.json` mantêm dados locais.
- `frontend/src/pages/`, `components/`, `context/` e `api/` compõem a SPA.
- `backend/tests/` contém testes unitários e de rotas.

## Comandos confirmados

- Backend: `cd backend && pip install -r requirements-dev.txt && pytest`.
- Frontend: `cd frontend && npm install && npm run build`.
- Desenvolvimento: `cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`; `cd frontend && npm run dev`.
- Não há comando/configuração de lint nem type checking nos manifests atuais. Como o frontend é JavaScript, não existe `tsconfig`; o backend também não configura mypy/pyright.

## LLM e prompts

- Provedores ficam em `backend/app/llm_assistant.py`: OpenAI Responses, Anthropic Messages, Google Gemini e xAI Grok, chamados diretamente por HTTP, com fallback local.
- Modelos, chaves por variável de ambiente, limites e persistência são tratados em `backend/app/llm_config.py`; configuração sensível local esperada em `backend/data/llm_config.json` (ignorada pelo Git).
- Não há um system prompt único. Prompts de sistema por tarefa estão inline nas funções de `backend/app/llm_assistant.py`; prompts de enriquecimento de busca também aparecem em `backend/app/tactical_search/llm_tactical_enrichment.py`. `docs/prompts.md` registra apenas direcionamentos gerais.

## Visão computacional e OCR

- `backend/app/video_vision.py` faz processamento local em CPU: amostragem, subtração de fundo, tracking, bola provável, homografia, eventos, grafos e key frames; `backend/app/video_analysis/` contém processamento, movimento e visualização adicionais.
- Key frames podem alimentar a análise LLM multimodal. Não há engine/biblioteca de OCR instalada: identificação textual é apresentada como hipótese e a própria implementação aponta OCR especializado como evolução.

## Busca

- `online_search.py`, `web_search.py`, `wikipedia_lookup.py`, `youtube_search.py` e `source_collector.py` coletam/consolidam fontes.
- `tactical_search/` adiciona orquestração, paralelismo, cache, retry, flags, recência, ranking, validação de vídeo, monitoramento e enriquecimento LLM. A rede possui fallback local; testes devem mocká-la.

## Pesquisa operacional

- `backend/app/operational_research.py` usa `networkx.max_weight_matching` para atribuição exata jogador-vaga e compara formações por índices ofensivo, defensivo e de equilíbrio.

## Testes e configuração

- `backend/pytest.ini` aponta para `backend/tests`; a suíte cobre rotas, LLM/configuração, busca, grafos, vídeo, pesquisa operacional, rate limit e logging.
- Configuração operacional vem de variáveis de ambiente, `render.yaml`, `Dockerfile` e defaults no código. Não foi encontrado `.env` versionado.

## Principais lacunas da avaliação

- Não há tool calling nativo/estruturado por LLM nem exemplos few-shot identificados.
- Parâmetros existem, mas faltam protocolo e resultados reprodutíveis de experimentos de modelos/prompts.
- Não existem lint e type checking configurados.
- README e arquitetura estão parcialmente desatualizados frente aos módulos atuais.
- Falta evidência consolidada sobre uso do agente e material de apresentação/demonstração orientado aos critérios.

