# Registro do Agente

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
