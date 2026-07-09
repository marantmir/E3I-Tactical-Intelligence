# Prompts usados com o agente de codificação

## Prompt 1 - Criação do projeto

```text
Crie uma aplicação chamada E3I Tactical Intelligence.

A aplicação será um protótipo para avaliação intermediária de IA Generativa. O objetivo é criar toda a interface e estrutura de uma plataforma de análise tática de futebol, sem integrar nenhum modelo de IA, LLM ou API externa.

Use:
- Backend Python com FastAPI
- Frontend React com Vite
- Banco local SQLite
- Dados mockados

A aplicação deve permitir buscar um time, visualizar dossiê tático simulado, elenco, formações, fontes e vídeos simulados, plano de jogo, relatório final e histórico.
```

## Prompt 2 - Backend

```text
Implemente o backend FastAPI da aplicação E3I Tactical Intelligence.

Regras obrigatórias:
- Não usar LLM
- Não integrar OpenAI, Gemini, Claude ou qualquer modelo
- Não integrar APIs externas
- Usar apenas dados mockados
- Criar endpoints REST organizados
- Usar SQLite para persistir histórico de análises

Crie endpoints para health, teams, search, tactical-analysis, formations, players, sources, game-plan, analysis, history e reports.
```

## Prompt 3 - Frontend

```text
Implemente o frontend React com Vite para a aplicação E3I Tactical Intelligence.

A aplicação deve ter sidebar, header, dashboard, nova análise, busca de times, dossiê tático, formações, elenco, fontes e vídeos simulados, plano de jogo, relatório final, histórico e tela explicando como a IA será integrada futuramente.
```

## Prompt 4 - Reforço para não usar IA real

```text
Revise o projeto inteiro e garanta que não exista nenhuma integração real com IA, LLM, OpenAI, Gemini, Claude, Hugging Face, LangChain ou APIs externas.

Todas as respostas táticas, fontes, vídeos, relatórios e recomendações devem ser mockadas.
```

## Prompt 5 - README e documentação

```text
Crie um README.md completo para o projeto E3I Tactical Intelligence seguindo uma rubrica acadêmica.

O README deve conter visão geral, problema, solução proposta, funcionalidades, tecnologias, arquitetura, como rodar localmente, endpoint, GitHub, dados mockados, explicação de que não há IA real, futura IA, prompts usados, o que funcionou, limitações e próximos passos.
```

## Prompt 6 - Checklist da avaliação

```text
Crie um arquivo docs/evaluation-checklist.md avaliando o projeto contra os critérios da avaliação intermediária: endpoint funcional, complexidade e ambição, GitHub, README e uso efetivo do agente de codificação.
```
