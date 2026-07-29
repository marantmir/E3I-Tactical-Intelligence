# Checklist da avaliação

| Critério | Situação atual | Correção necessária | Status | Evidência |
| -------- | -------------- | ------------------- | ------ | --------- |
| Tool calling | Provedores são chamados por HTTP e recebem texto/JSON; não há ferramentas declaradas para o modelo. | Definir caso real, schemas, execução segura e testes do ciclo de ferramentas. | Lacuna | `backend/app/llm_assistant.py` |
| Few-shot | Prompts por tarefa existem, sem exemplos de entrada/saída identificados. | Adicionar exemplos somente onde um experimento demonstrar ganho. | Lacuna | `backend/app/llm_assistant.py`; `backend/app/tactical_search/llm_tactical_enrichment.py` |
| Parâmetros | Provider, modelo, timeout, temperatura, tokens e controles de análise são configuráveis e validados. | Documentar justificativas/defaults e sua relação com resultados. | Parcial | `backend/app/llm_config.py`; `frontend/src/pages/FutureAI.jsx` |
| Experimentos | Não há benchmark versionado, matriz de modelos/prompts ou resultados reproduzíveis. | Criar dataset, métricas, baseline, protocolo offline e relatório. | Lacuna | Ausência em `docs/` e testes |
| Arquitetura | Full stack modular, fallbacks, busca, CV e otimização existem; documento não cobre toda a implementação atual. | Atualizar diagrama, fluxos LLM/busca/vídeo e limites. | Parcial | `docs/architecture.md`; `backend/app/`; `frontend/src/` |
| README | Explica execução e funções principais, mas não registra lint/type check inexistentes nem avaliação reprodutível. | Alinhar arquitetura, comandos e evidências depois das correções. | Parcial | `README.md`; `frontend/package.json`; `backend/pytest.ini` |
| Uso do agente | Há registro narrativo de entregas, sem protocolo completo ou rastreabilidade por critério. | Documentar processo, prompts/fases, decisões e validações sem expor segredos. | Parcial | `docs/agent-log.md`; `docs/prompts.md` |
| Apresentação | A SPA oferece telas e visualizações; não há roteiro/demo de avaliação consolidado. | Criar narrativa, roteiro verificável e material visual após estabilizar os critérios. | Parcial | `frontend/src/pages/`; `frontend/src/components/` |
