# E3I Tactical Intelligence

## Visão Geral

O **E3I Tactical Intelligence** é uma aplicação web para apoiar **scouts, treinadores, analistas de desempenho e comissões técnicas** na preparação de jogos e análise de adversários.

A aplicação permite que o usuário digite o nome de um time de futebol e visualize um **dossiê tático simulado**, contendo informações sobre:

- Perfil do clube
- Últimos jogos
- Formações mais utilizadas
- Jogadores-chave
- Pontos fortes
- Fragilidades
- Sugestões de plano de jogo
- Relatório final para comissão técnica

Nesta etapa da avaliação, a aplicação **não integra nenhum modelo de IA/LLM real**. Todas as análises táticas, recomendações e relatórios são gerados por meio de **dados mockados e respostas simuladas**, representando como a IA seria integrada futuramente.

## Problema Escolhido

Clubes, treinadores e analistas precisam estudar adversários com rapidez, qualidade e profundidade. Porém, as informações sobre um time geralmente ficam espalhadas em várias fontes: notícias, vídeos, estatísticas, escalações, histórico de jogos e observações técnicas.

Esse processo pode ser demorado e manual, principalmente para clubes menores, analistas independentes e categorias de base que não possuem acesso a plataformas caras de análise esportiva.

O problema que a aplicação busca resolver é:

> Como transformar dados dispersos sobre um time de futebol em um dossiê tático organizado, visual e acionável para apoiar preparação de jogo, scouting e tomada de decisão?

## Solução Proposta

A solução proposta é uma plataforma web que centraliza a análise de um time em uma interface única.

O usuário informa o nome do clube desejado e o sistema apresenta um painel com dados simulados, análises táticas e recomendações práticas.

A aplicação funciona como um protótipo de uma futura solução com IA generativa, onde futuramente seriam integradas fontes como:

- APIs esportivas
- Notícias da internet
- Dados estatísticos de partidas
- Vídeos públicos
- Uploads de vídeos próprios
- Bases históricas de clubes
- Modelos de linguagem para gerar análises táticas
- Modelos de visão computacional para análise de vídeo

## Stack

- Backend: FastAPI, SQLAlchemy e SQLite
- Frontend: React com Vite
- Banco local: `backend/e3i_tactical.db`

## Estrutura de Pastas

```text
e3i-tactical-intelligence/
  backend/
    app/
      routers/
      services/
      database.py
      main.py
      models.py
      schemas.py
    requirements.txt
  frontend/
    src/
      App.jsx
      main.jsx
      styles.css
    index.html
    package.json
  .gitignore
  README.md
```

## Como Rodar Localmente

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

No Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API roda em `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend roda em `http://127.0.0.1:5173`.

## Endpoints

- `GET /health` - verifica a saúde da API
- `POST /api/analyses` - cria uma análise tática mockada
- `GET /api/analyses` - lista análises salvas
- `GET /api/analyses/{analysis_id}` - consulta uma análise salva

Exemplo de request:

```json
{
  "club_name": "Palmeiras"
}
```

## Como a IA Será Integrada Futuramente

Na versão futura, a IA será usada para:

1. Buscar e resumir informações sobre o clube.
2. Analisar notícias, textos e relatórios.
3. Interpretar dados estatísticos de partidas.
4. Sugerir formações prováveis.
5. Identificar padrões ofensivos e defensivos.
6. Gerar relatórios para scouts e treinadores.
7. Sugerir estratégias para enfrentar o adversário.
8. Resumir vídeos e destacar padrões táticos.
9. Criar planos de treino baseados nas fragilidades do adversário.

Nesta avaliação, esses recursos aparecem apenas como **simulações visuais e funcionais**, usando dados fictícios ou pré-cadastrados.

## Observações

- O banco SQLite é criado automaticamente quando o backend inicia.
- Clubes mockados: Palmeiras, Flamengo, São Paulo, Corinthians e Fluminense.
- Clubes desconhecidos recebem um perfil tático genérico simulado.
