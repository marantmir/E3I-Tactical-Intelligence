# Arquitetura

## Visão geral

O E3I Tactical Intelligence foi estruturado como uma aplicação web full stack com frontend React, backend FastAPI e persistência local em SQLite.

```text
Usuário
  -> Frontend React/Vite
  -> Cliente HTTP
  -> Backend FastAPI
  -> SQLite para histórico
  -> JSON mockado para dados táticos
```

## Backend

O backend fica em `backend/app` e expõe rotas sob `/api`.

Arquivos principais:

- `main.py`: inicializa FastAPI, CORS, rotas e frontend buildado.
- `database.py`: cria e consulta histórico em SQLite.
- `mock_store.py`: carrega dados mockados em JSON.
- `routes/teams.py`: endpoints de times e análises por time.
- `routes/analysis.py`: criação de análise e histórico.
- `routes/reports.py`: relatório final simulado.

## Frontend

O frontend fica em `frontend/src`.

Principais telas:

- Dashboard
- Nova análise
- Busca de time
- Dossiê tático
- Formações
- Elenco
- Fontes e vídeos simulados
- Plano de jogo
- Relatório final
- Histórico
- Como a IA será integrada

## Dados

Os dados táticos são mockados e ficam em `backend/mock_data`.

O banco SQLite guarda somente o histórico criado na aplicação.

## Deploy

O `Dockerfile` cria o build React e serve os arquivos estáticos pelo FastAPI. Assim, um único endpoint público abre a interface e responde às rotas `/api`.

## Evolução futura

Em versões futuras, a arquitetura pode receber módulos especializados para:

- Grafos táticos: análise de redes de passe, conexões entre jogadores e zonas de influência.
- Visão computacional: detecção de jogadores, bola, linhas, compactação e movimentações em vídeo.
- Pesquisa operacional: otimização de formação, estratégia, tática, substituições e planos por cenário.

Esses módulos devem continuar separados da camada de interface e expor resultados por endpoints próprios, sempre com nível de confiança e rastreabilidade das evidências.
