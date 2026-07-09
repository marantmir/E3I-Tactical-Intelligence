# E3I Tactical Intelligence

## 1. Visão Geral

O E3I Tactical Intelligence é um protótipo de aplicação web para análise tática de times de futebol. O objetivo é apoiar scouts, treinadores, analistas de desempenho e comissões técnicas na organização de informações sobre adversários, jogadores, fontes e planos de jogo.

Nesta versão, a aplicação não utiliza modelos de IA ou LLMs. As análises táticas continuam simuladas com dados mockados, mas o fluxo de nova análise inclui uma busca pública online opcional para enriquecer a pré-análise com informações abertas sobre o time.

## 2. Problema

A preparação de jogos e a análise de adversários exigem consulta a várias fontes, como estatísticas, vídeos, notícias, escalações e relatórios técnicos. Esse processo costuma ser manual, demorado e pouco padronizado, especialmente para clubes menores, categorias de base e analistas independentes.

O problema tratado é: como organizar informações dispersas sobre um time em um dossiê tático visual, estruturado e acionável?

## 3. Solução Proposta

A aplicação permite buscar um time e visualizar um dossiê tático simulado com:

- Perfil do clube
- Formação base e formações alternativas
- Modelo ofensivo e defensivo
- Elenco e jogadores-chave
- Fontes e vídeos simulados
- Plano de jogo
- Pré-análise antes de salvar
- Busca pública online opcional
- Relatório final
- Histórico de análises
- Tela explicando futura integração com IA

## 4. Importante: Sem Integração Real com IA

Este projeto é um protótipo acadêmico desenvolvido para a Avaliação Intermediária de IA Generativa. A aplicação não utiliza modelos de IA ou LLMs nesta versão. As análises, vídeos e recomendações continuam simulados com dados mockados. A busca online é usada apenas como enriquecimento público opcional na pré-análise e não substitui validação humana.

## 5. Como a IA será integrada futuramente

Em uma próxima versão, a IA poderá ser usada para:

- Buscar informações em fontes públicas e APIs esportivas
- Resumir notícias e relatórios
- Analisar transcrições de vídeos
- Aplicar visão computacional para detectar movimentações, ocupação de espaço e padrões coletivos
- Usar grafos para mapear conexões de passe, zonas de influência e relações táticas
- Usar pesquisa operacional para otimizar formação, estratégia, tática e substituições por cenário
- Gerar dossiês táticos com base em evidências
- Sugerir formações prováveis
- Identificar padrões ofensivos e defensivos
- Recomendar planos de jogo
- Apoiar scouting de jogadores
- Criar relatórios personalizados para comissão técnica

## 6. Tecnologias Utilizadas

- Python
- FastAPI
- SQLite
- React
- Vite
- JavaScript
- CSS
- Docker
- Render, Railway ou Hugging Face Spaces para deploy

## 7. Arquitetura

O frontend em React fornece a interface, navegação, formulários, tabelas e visualizações. O backend em FastAPI fornece endpoints para times, jogadores, análises táticas, fontes, plano de jogo, relatórios, histórico, pré-análise e busca pública online opcional.

O SQLite é usado para persistir o histórico de análises criadas pelo usuário. O restante da base é mockado em arquivos JSON dentro de `backend/mock_data`.

```text
Usuário
  -> Frontend React
  -> Serviços HTTP
  -> Backend FastAPI
  -> SQLite e dados mockados
  -> Interface visual
```

## 8. Funcionalidades Implementadas

- Dashboard inicial com indicadores simulados
- Busca de times
- Formulário de nova análise
- Botão Analisar antes de salvar
- Pré-análise com insights de grafos, visão computacional e pesquisa operacional
- Busca pública online opcional sobre o time analisado
- Dossiê tático
- Análise de formações
- Análise de elenco com filtros
- Fontes e vídeos simulados
- Plano de jogo
- Relatório final
- Histórico de análises
- Página "Como a IA será integrada"

## 9. Como Rodar Localmente

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

No Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Aplicação unificada

Para produção, o `Dockerfile` builda o frontend e serve o build pelo FastAPI. A rota `/` abre a interface e as rotas `/api` respondem pelo backend.

O passo a passo de publicação está em:

```text
docs/deploy.md
```

O roadmap avançado de grafos, visão computacional e pesquisa operacional está em:

```text
docs/advanced-decision-roadmap.md
```

## 10. Endpoint Público

Endpoint da aplicação:

```text
INSERIR_LINK_DO_ENDPOINT_AQUI
```

## 11. Repositório GitHub

```text
https://github.com/marantmir/e3i-tactical-intelligence
```

## 12. Dados Mockados

Os dados utilizados são fictícios e foram criados apenas para demonstrar o funcionamento do protótipo.

Eles incluem:

- Times
- Jogadores
- Formações
- Análises táticas
- Fontes simuladas
- Vídeos simulados
- Planos de jogo
- Relatórios

## 13. Uso do Agente de Codificação

O projeto foi desenvolvido com apoio de um agente de codificação. Foram usados prompts para criar a estrutura inicial, implementar backend FastAPI, criar dados mockados, implementar frontend React, ajustar layout, corrigir bugs e documentar o projeto.

Os prompts utilizados estão documentados em:

```text
docs/prompts.md
```

O registro das interações está em:

```text
docs/agent-log.md
```

Evidências visuais da aplicação estão em:

```text
docs/screenshots/
```

## 14. O que Funcionou Bem

- A estrutura FastAPI + React permitiu separar API, telas e dados mockados.
- Os dados JSON mantêm o protótipo funcional mesmo se a busca online estiver indisponível.
- O SQLite resolveu a necessidade de histórico local.
- A navegação por telas aumentou a complexidade da entrega sem usar IA real.
- O fluxo de pré-análise permitiu revisar informações e insights antes de salvar.

## 15. O que Não Funcionou Bem

- O escopo inicial pedia muitos fluxos, então foi necessário priorizar uma versão funcional e demonstrável.
- A exportação em PDF ficou simulada nesta etapa.
- Os dados são fictícios e não devem ser interpretados como avaliação real de clubes ou atletas.

## 16. Intervenções Manuais

- Remoção de qualquer integração real com IA.
- Inclusão de busca pública online opcional com fallback para dados mockados.
- Definição de uma base mockada estável.
- Padronização da navegação.
- Ajuste de telas para rubrica acadêmica.
- Criação de documentação de prompts e decisões.

## 17. Limitações do Protótipo

- A busca online usa fonte pública aberta e pode falhar conforme disponibilidade de rede.
- Não há integração com YouTube.
- Não há modelo de IA.
- Não há análise real de vídeo.
- Os dados são simulados.
- A pré-análise combina informações públicas com insights táticos mockados.
- A exportação PDF é placeholder visual.
- As recomendações táticas são mockadas.

## 18. Próximos Passos

- Integrar APIs esportivas.
- Adicionar busca real de notícias.
- Integrar YouTube Data API.
- Adicionar RAG com fontes confiáveis.
- Integrar LLM para geração dos relatórios.
- Permitir upload de vídeos.
- Adicionar transcrição automática.
- Implementar análise visual com visão computacional.
- Implementar análise via grafos para conexões de passe, zonas de influência e movimentações.
- Usar pesquisa operacional para apoiar melhor formação, estratégia, tática e substituições.
- Criar ranking de jogadores para scouting.
- Exportar PDF real.
