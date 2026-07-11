# E3I Tactical Intelligence

Aplicacao web para inteligencia tatica de futebol. O fluxo prioriza videos de partidas, gera pre-analise visual, revisa evidencias, visualiza grafos taticos, analisa movimentos e salva o dossie no historico local.

## Funcionalidades

- Selecao global de time ativo para consumir dados locais, fontes salvas e pendencias de coleta nas telas.
- Busca publica restrita a materiais taticos e videos analisaveis.
- Pre-analise antes do salvamento.
- Analise por grafos com conexoes entre rastros, zonas, centralidade e densidade.
- Leitura visual de videos com mapa de calor, trilhas de movimento, bola provavel, homografia aproximada, eventos e recomendacoes.
- Pesquisa operacional para comparar formacao, risco, estrategia e ajustes por cenario.
- Relatorio final consolidado para comissao tecnica.
- Historico persistido em SQLite.

## Arquitetura

```text
Frontend React/Vite
  -> cliente HTTP
Backend FastAPI
  -> busca publica tatica/video
  -> data_store JSON local
  -> graph_analysis
  -> video_vision
  -> SQLite
```

## Como Rodar

Backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend em desenvolvimento:

```powershell
cd frontend
npm install
npm run dev
```

Build servido pelo FastAPI:

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Testes automatizados do backend:

```powershell
cd backend
pip install -r requirements-dev.txt
pytest
```

## Deploy Web

O projeto esta preparado para deploy Docker usando `Dockerfile` e `render.yaml`.

Guia completo:

```text
DEPLOY.md
```

Resumo para Render:

1. Suba o codigo para `https://github.com/marantmir/E3I-Tactical-Intelligence`.
2. Crie um `Blueprint` no Render apontando para o repositorio.
3. Configure `OPENAI_API_KEY` como secret, se quiser usar LLM real.
4. Publique e valide `/api/health`.

## Endpoints Principais

- `GET /api/teams`
- `GET /api/teams/options`
- `GET /api/teams/workspace/{team_ref}`
- `GET /api/teams/search?query=...`
- `GET /api/teams/{team_id}/public-intelligence`
- `GET /api/teams/{team_id}/graph-analysis`
- `POST /api/teams/{team_id}/video-vision/upload`
- `POST /api/analysis/preview`
- `POST /api/analysis`
- `GET /api/history`
- `POST /api/reports`

## Observacoes Tecnicas

A busca publica evita dados institucionais e foca em materiais taticos, videos de jogos e analises publicas. Se a rede externa estiver bloqueada, o sistema preserva o fluxo com links estruturados para coleta manual.

As visualizacoes de grafos e videos sao calculadas no backend a partir do conteudo visual disponivel e exibidas no frontend como apoio a decisao tecnica.

### Camada LLM opcional

O backend usa uma camada LLM opcional para enriquecer consultas de busca, pre-analises, leitura tatica do video e hipoteses de identificacao de time/jogador/numero. Sem chave de API, o sistema continua operando com fallback local deterministico.

Pelo app, acesse `IA avancada` (`/future-ai`) para parametrizar:

- habilitar/desabilitar uso da LLM;
- informar API key;
- selecionar modelo;
- ajustar timeout, temperatura e limite de tokens;
- definir idioma, profundidade, escopo de busca e modo de identificacao visual.

As configuracoes locais ficam em `backend/data/llm_config.json`, arquivo ignorado pelo Git por poder conter chave de API.

```powershell
$env:OPENAI_API_KEY="sua_chave"
$env:OPENAI_MODEL="gpt-4.1-mini"
$env:E3I_LLM_TIMEOUT_SECONDS="18"
```

Tambem e possivel configurar por variaveis de ambiente. O modelo nunca deve inventar nomes de jogadores: quando OCR/crops da camisa nao forem suficientes, a interface mantem a identidade como "nao identificado" e orienta a confirmacao visual.

Repositorio alvo: `https://github.com/marantmir/e3i-tactical-intelligence`
