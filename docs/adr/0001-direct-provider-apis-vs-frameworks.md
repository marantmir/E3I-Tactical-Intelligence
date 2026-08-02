# ADR 0001: APIs diretas de provedores versus frameworks

- **Status:** aceito
- **Data:** 2026-08-02
- **Decisão:** manter adaptadores HTTP diretos e um contrato interno neutro.

## Contexto

O produto tem quatro provedores opcionais, tool calling delimitado, entrada multimodal compacta, fallback local e testes que não podem usar rede. O fluxo é curto e conhecido; transparência do payload, timeout e custo é mais valiosa agora que composição dinâmica de agentes.

## Comparação

| Critério | API direta | LangChain | LlamaIndex | Semantic Kernel |
|---|---|---|---|---|
| Complexidade | baixa, código explícito | alta abstração | média/alta, orientada a RAG | média/alta, plugins/planners |
| Dependências | HTTP/Pydantic existentes | grafo amplo de pacotes | amplo para índices/conectores | SDK e ecossistema próprios |
| Lock-in | contrato interno controlado | APIs do framework | modelos de índice/query engine | conceitos Kernel/plugin |
| Tool calling | adaptadores mantidos aqui | amplo e conveniente | disponível, secundário a RAG | forte |
| Multimodalidade | payload por provedor, já implementado | varia por integração | varia por modelo/conector | varia por conector |
| Observabilidade | eventos mínimos sob controle | callbacks/tracing maduros | tracing disponível | filtros/telemetria fortes |
| Testabilidade | MockTransport e fixtures diretas | exige mocks de camadas | exige montar componentes | exige montar Kernel/conectores |
| Custo runtime | menor overhead | mais indireção/tokens possíveis | custo de ingestão/índice | indireção de orquestração |
| Aprendizagem | HTTP dos 4 provedores | DSL/ecossistema LangChain | conceitos de RAG | conceitos SK/.NET/Python |
| Manutenção | acompanhar 4 protocolos | acompanhar framework + providers | framework + índices/providers | SDK + connectors/providers |

## Consequências

A solução preserva payloads auditáveis, dependências leves, fallback determinístico e testes herméticos. Em contrapartida, a equipe mantém mudanças de protocolo, normalização, retries e observabilidade básica. Não se afirma que frameworks sejam inadequados em geral: LlamaIndex é atraente para RAG documental; LangChain para ecossistema de integrações; Semantic Kernel para organizações já padronizadas em plugins e planners Microsoft.

## Condições objetivas para reavaliação

Registrar uma nova ADR e executar um spike comparável quando **qualquer** condição ocorrer:

1. três ou mais novos tipos de integração repetirem pelo menos 200 linhas de adaptação;
2. houver fluxo com mais de oito etapas dinâmicas ou planejamento concorrente;
3. RAG exigir mais de duas bases vetoriais/conectores e pipeline de ingestão;
4. observabilidade atual não permitir diagnosticar pelo menos 95% das falhas em amostra mensal;
5. manutenção dos adaptadores consumir mais de 20% da capacidade do time por dois ciclos;
6. um framework reduzir ao menos 30% do código/tempo em spike, sem regredir suíte hermética, latência p95 em mais de 10%, segurança ou custo por execução.
