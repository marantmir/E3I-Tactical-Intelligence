# Checklist final de avaliação

Auditoria executada em 2 de agosto de 2026. Os estados abaixo têm somente os
valores permitidos e apontam para evidências produzidas nesta execução.

| Critério | Estado | Evidência corrente | Ação para conclusão |
|---|---|---|---|
| Visão, arquitetura, instalação, execução e testes no README | ATENDIDO | Seções e comandos locais revisados; links relativos aprovados pelo quality gate. | Manter o verificador de links no gate. |
| Tool calling modelo → tool → modelo | ATENDIDO | Suíte hermética e teste focal do orquestrador aprovados. | Manter os testes como proteção de regressão. |
| Duas tools sequenciais e preservação do contexto | ATENDIDO | Casos do orquestrador e de tools táticas aprovados. | Manter os testes como proteção de regressão. |
| Limite de iterações de 1 a 8, padrão 4 | ATENDIDO | Casos de configuração e interrupção do loop aprovados. | Manter os testes como proteção de regressão. |
| Tool inexistente, argumentos inválidos, timeout e erro sanitizado | ATENDIDO | Casos negativos do registro/orquestrador aprovados. | Manter os testes como proteção de regressão. |
| Seis tools táticas com schemas fechados e limites | ATENDIDO | Registro e wrappers cobertos pela suíte hermética. | Exigir registro e teste equivalente para qualquer tool nova. |
| Quatro adaptadores nativos de provedor | ATENDIDO | OpenAI Responses, Anthropic Messages, Gemini e xAI cobertos com transporte mockado. | Manter os contratos mockados no gate. |
| Fallback entre provedores mockados e fallback local | ATENDIDO | Rotas, limite de tentativas e ausência de credenciais cobertos offline. | Manter os casos de falha no gate. |
| Prompt runtime com três few-shots | ATENDIDO | Teste estrutural do prompt aprovado. | Atualizar teste e documentação em qualquer mudança de prompt. |
| Schema estruturado, parsing, reparo único e fallback | ATENDIDO | Casos válidos e inválidos aprovados offline. | Manter os casos de contrato no gate. |
| Experimento offline em JSON, CSV e Markdown | ATENDIDO | 20 casos regenerados; três artefatos produzidos. | Regenerar artefatos com o runner oficial antes de cada entrega. |
| Ausência de chamadas online na validação | ATENDIDO | Runner executado com `RUN_ONLINE_LLM_EXPERIMENTS=false`; transportes externos mockados. | Preservar a execução hermética no CI. |
| Build frontend e compilação backend | ATENDIDO | Vite transformou 1.629 módulos; `compileall` terminou sem erro. | Manter ambos no `make validate`. |
| Lint e verificação estática disponível | ATENDIDO | Parser AST/compileall e lint frontend aprovados. | Adotar mypy/pyright em etapa futura, com migração tipada dedicada. |
| Auditoria de dependências local | PARCIAL | `pip check` e `npm audit --offline` aprovados; não houve consulta online de CVEs. | Em runner com rede, executar `python -m pip install pip-audit && python -m pip_audit -r backend/requirements.txt -r backend/requirements-dev.txt` e `npm --prefix frontend audit --audit-level=high`; anexar a saída atual. |
| Scanner de segredos e arquivos sensíveis | ATENDIDO | Verificações locais aprovaram conteúdo e nomes; nenhum segredo conhecido versionado. | Manter checks locais e Gitleaks no histórico do CI. |
| Links relativos | ATENDIDO | Verificador local aprovou todos os Markdown rastreados. | Manter o check no gate. |
| Health check local | ATENDIDO | Requisição local isolada retornou HTTP 200; a rota também é coberta pela suíte FastAPI. | Repetir no ambiente de deploy antes da publicação. |
| Experimentos com provedores reais | NÃO VERIFICÁVEL | Credenciais e rede são deliberadamente excluídas da validação hermética. | Em staging autorizado, configurar credenciais efêmeras, executar a matriz documentada três vezes por configuração, registrar custo/latência e remover as credenciais ao terminar. |
| Endpoint público e console em produção | NÃO VERIFICÁVEL | Nenhum deploy público foi fornecido nesta execução. | Publicar em staging, executar health check, percorrer o fluxo em navegador e anexar URL, data, console e resultado. |
| Firewall/proxy de egress e armazenamento multi-instância | NÃO ATENDIDO | São controles de infraestrutura fora do repositório atual. | Provisionar allowlist de egress e storage compartilhado, documentar a configuração e validar falha fechada em staging. |
| Push da branch | NÃO ATENDIDO | Não há remote Git configurado. | Executar `git remote add origin <URL_DO_REPOSITORIO>` e `git push -u origin fix/final-evaluation-compliance`; registrar a saída real. |
| Pull request | NÃO ATENDIDO | Não há remote `origin` e o GitHub CLI não está instalado. | Depois do push, executar `gh pr create --base main --head fix/final-evaluation-compliance --title "Final evaluation compliance and native tool calling" --body-file docs/pull-request-summary.md`; registrar a URL real, sem merge automático. |
| Apresentação gravada e validada por pessoa | NÃO ATENDIDO | Status da apresentação: pendente de gravação e validação humana. | Seguir `presentation-checklist.md`, gravar 5–8 minutos, obter revisão humana e registrar o artefato aprovado. |

O resultado do teste obrigatório sem adaptação de ambiente é **PARCIAL**: o
Python ativo não contém `httpx`, apesar de a dependência estar declarada. O gate
completo foi repetido reutilizando a instalação local isolada do Poetry e aprovou
535 testes, sem rede ou alteração de dependências do projeto.

## Ordem de fechamento

1. Configurar um remote válido e publicar a branch sem force push.
2. Criar o pull request usando o resumo versionado e aguardar todos os checks.
3. Executar auditorias online e validações de staging; atualizar estados somente
   depois de anexar saídas produzidas nessa execução.
4. Gravar a apresentação, aplicar a revisão humana e registrar o artefato.

Um item só muda para **ATENDIDO** quando a evidência descrita na respectiva ação
existir. A existência de uma ação planejada, isoladamente, não altera o estado.
