# Experimentos offline reproduzíveis

## Objetivo e estrutura

Este pacote compara, sem rede ou credenciais, dez dimensões do fluxo LLM: few-shot, schema, uso e sequência de tools, suficiência de evidência, timeout, fallback, criatividade, tool inexistente e completude semântica. `fixtures/` contém entradas e resultados esperados fixos; `runners/` contém o executor em biblioteca padrão; `schemas/` publica o contrato da saída; e `results/` guarda somente os três relatórios auditáveis mais recentes.

As 20 execuções (duas variantes por dimensão) reutilizam o texto, as métricas, os frames simulados e as respostas de tools de `fixtures/offline_cases.json`. Identificadores são estáveis, dados são sintéticos e cada caso documenta `expected` e `obtained`. O mock não pretende simular qualidade probabilística de um provedor: ele torna verificáveis orquestração, cálculo e serialização.

## Métricas

Todas as taxas têm denominador igual ao total de casos, salvo conflito:

- **Resposta válida:** casos com validade sintática e semântica / casos.
- **Aderência ao schema:** casos que obedecem ao contrato / casos.
- **Grounding:** casos cujas afirmações apontam para evidência fornecida / casos.
- **Uso correto de tools:** seleção/erro de tool corretamente tratado / casos.
- **Fallback:** casos que acionaram fallback / casos (incidência, não pontuação de qualidade).
- **Média de iterações:** soma das iterações / casos.
- **Latência offline:** duração lógica normalizada em milissegundos; é zero para preservar reprodutibilidade e não representa rede.
- **Erros por cenário:** quantidade em que `obtained` difere de `expected`, agrupada por cenário.
- **Conclusão:** casos semanticamente completos / casos.
- **Conflito sinalizado corretamente:** conflitos esperados sinalizados / casos que esperavam conflito.

## Comandos

Execute da raiz:

```bash
RUN_ONLINE_LLM_EXPERIMENTS=false python experiments/runners/run_offline.py
python -m pytest -q backend/tests/test_offline_experiments.py
```

O runner sobrescreve deterministicamente `latest.json`, `latest.csv` e `latest.md`. Um valor diferente de `false` para a variável online encerra a execução, em vez de acessar a rede.

## Limitações e futura execução online

Os resultados medem fixtures, um mock determinístico e regras locais; não medem acurácia, custo, tokens nem latência de provedores. **Experimentos online: não executados.** Para habilitá-los futuramente, deve-se implementar um runner separado, revisão de segurança/privacidade, orçamento, consentimento explícito e armazenamento de proveniência. Somente então uma execução deliberada poderia usar `RUN_ONLINE_LLM_EXPERIMENTS=true`; o runner atual continuará recusando esse valor e nenhuma chave deve ser versionada.
