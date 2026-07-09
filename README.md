# E3I Tactical Intelligence

Aplicacao web para inteligencia tatica de futebol. O fluxo permite pesquisar um time, gerar uma pre-analise com busca publica, revisar evidencias, visualizar grafos taticos, analisar movimentos em videos e salvar o dossie no historico local.

## Funcionalidades

- Busca local e publica sobre o time analisado.
- Pre-analise antes do salvamento.
- Dossie tatico, elenco, formacoes, fontes e plano de jogo.
- Analise por grafos com conexoes entre jogadores, zonas, centralidade e densidade.
- Leitura visual de videos com mapa de calor, trilhas de movimento, eventos e recomendacoes.
- Pesquisa operacional para comparar formacao, risco, estrategia e ajustes por cenario.
- Relatorio final consolidado para comissao tecnica.
- Historico persistido em SQLite.

## Arquitetura

```text
Frontend React/Vite
  -> cliente HTTP
Backend FastAPI
  -> busca publica Wikimedia
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

## Endpoints Principais

- `GET /api/teams`
- `GET /api/teams/search?query=...`
- `GET /api/teams/{team_id}/public-intelligence`
- `GET /api/teams/{team_id}/graph-analysis`
- `GET /api/teams/{team_id}/video-vision`
- `POST /api/analysis/preview`
- `POST /api/analysis`
- `GET /api/history`
- `POST /api/reports`

## Observacoes Tecnicas

A busca publica usa APIs abertas da Wikimedia quando a rede esta disponivel. Se a rede externa estiver bloqueada, o sistema preserva o fluxo com modo local e apresenta uma fonte publica sugerida para validacao manual.

As visualizacoes de grafos e videos sao calculadas no backend a partir das evidencias disponiveis e exibidas no frontend como apoio a decisao tecnica.

Repositorio alvo: `https://github.com/marantmir/e3i-tactical-intelligence`
