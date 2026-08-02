# Checklist final de avaliação

Auditoria executada em 2 de agosto de 2026. Os estados abaixo têm somente os
valores permitidos e apontam para evidências produzidas nesta execução.

| Critério | Estado | Evidência corrente |
|---|---|---|
| Visão, arquitetura, instalação, execução e testes no README | ATENDIDO | Seções e comandos locais revisados; links relativos aprovados pelo quality gate. |
| Tool calling modelo → tool → modelo | ATENDIDO | Suíte hermética e teste focal do orquestrador aprovados. |
| Duas tools sequenciais e preservação do contexto | ATENDIDO | Casos do orquestrador e de tools táticas aprovados. |
| Limite de iterações de 1 a 8, padrão 4 | ATENDIDO | Casos de configuração e interrupção do loop aprovados. |
| Tool inexistente, argumentos inválidos, timeout e erro sanitizado | ATENDIDO | Casos negativos do registro/orquestrador aprovados. |
| Seis tools táticas com schemas fechados e limites | ATENDIDO | Registro e wrappers cobertos pela suíte hermética. |
| Quatro adaptadores nativos de provedor | ATENDIDO | OpenAI Responses, Anthropic Messages, Gemini e xAI cobertos com transporte mockado. |
| Fallback entre provedores mockados e fallback local | ATENDIDO | Rotas, limite de tentativas e ausência de credenciais cobertos offline. |
| Prompt runtime com três few-shots | ATENDIDO | Teste estrutural do prompt aprovado. |
| Schema estruturado, parsing, reparo único e fallback | ATENDIDO | Casos válidos e inválidos aprovados offline. |
| Experimento offline em JSON, CSV e Markdown | ATENDIDO | 20 casos regenerados; três artefatos produzidos. |
| Ausência de chamadas online na validação | ATENDIDO | Runner executado com `RUN_ONLINE_LLM_EXPERIMENTS=false`; transportes externos mockados. |
| Build frontend e compilação backend | ATENDIDO | Vite transformou 1.629 módulos; `compileall` terminou sem erro. |
| Lint e verificação estática disponível | ATENDIDO | Parser AST/compileall e lint frontend aprovados. |
| Auditoria de dependências local | PARCIAL | `pip check` e `npm audit --offline` aprovados; não houve consulta online de CVEs. |
| Scanner de segredos e arquivos sensíveis | ATENDIDO | Verificações locais aprovaram conteúdo e nomes; nenhum segredo conhecido versionado. |
| Links relativos | ATENDIDO | Verificador local aprovou todos os Markdown rastreados. |
| Health check local | ATENDIDO | `/api/health` é exercitado pela suíte FastAPI aprovada. |
| Experimentos com provedores reais | NÃO VERIFICÁVEL | Credenciais e rede são deliberadamente excluídas da validação hermética. |
| Endpoint público e console em produção | NÃO VERIFICÁVEL | Nenhum deploy público foi fornecido nesta execução. |
| Firewall/proxy de egress e armazenamento multi-instância | NÃO ATENDIDO | São controles de infraestrutura fora do repositório atual. |
| Push da branch | NÃO ATENDIDO | Não há remote Git configurado. |
| Pull request | NÃO ATENDIDO | Não há remote `origin` e o GitHub CLI não está instalado. |
| Apresentação gravada e validada por pessoa | NÃO ATENDIDO | Status da apresentação: pendente de gravação e validação humana. |

O resultado do teste obrigatório sem adaptação de ambiente é **PARCIAL**: o
Python ativo não contém `httpx`, apesar de a dependência estar declarada. O gate
completo foi repetido reutilizando a instalação local isolada do Poetry e aprovou
535 testes, sem rede ou alteração de dependências do projeto.
