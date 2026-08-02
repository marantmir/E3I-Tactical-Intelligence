# Roteiro de apresentação (5–8 minutos)

**Status da apresentação: pendente de gravação e validação humana.**

## 0:00–0:35 — Problema

Apresentar a dificuldade de transformar fontes dispersas, vídeo e métricas em
decisões táticas rastreáveis. Destacar que uma resposta convincente não basta:
ela precisa ser grounded, estruturada, reproduzível e segura.

## 0:35–1:05 — Solução

Mostrar o E3I como fluxo de inteligência: selecionar adversário, coletar fontes,
analisar evidências, calcular sinais táticos e produzir plano/relatório. Explicar
o modo local determinístico quando integrações opcionais não estão disponíveis.

## 1:05–1:40 — Arquitetura e fluxo principal

Abrir `docs/architecture.md`: frontend React/Vite → API FastAPI → serviços de
busca, vídeo, métricas e persistência. Narrar o fluxo pesquisa → pré-análise →
evidências → confronto/plano → relatório, sem confundir UI com garantia analítica.

## 1:40–2:30 — Prompt runtime e tool calling

Mostrar `backend/app/structured_llm.py`: regras de grounding, distinção entre
fato/inferência/hipótese, confiança, limitações e três few-shots. Em seguida,
mostrar `llm_tool_orchestrator.py`: modelo solicita uma tool, o registro valida e
executa, o resultado correlacionado volta ao mesmo histórico e o modelo conclui.
Mencionar limite de iterações, timeout, erro sanitizado e fallback.

## 2:30–3:20 — Tools táticas e provedores

Apontar as seis tools: busca tática, OCR, frames, métricas, pesquisa operacional
e contexto do time. Mostrar schemas fechados no registro. Resumir os quatro
adaptadores: OpenAI Responses, Anthropic Messages, Google Gemini e xAI, todos
testados com transporte mockado; não alegar validação paga/online.

## 3:20–4:00 — Experimento offline

Executar o runner e abrir os três artefatos. Explicar os 20 casos fixos e o valor
de comparar esperado/obtido sem credenciais, custo, instabilidade ou rede. Deixar
claro que isso valida contratos, não a qualidade de modelos reais.

## 4:00–4:40 — Segurança

Demonstrar allowlist, validação DNS/redirect, limites e logs de metadados. Mostrar
scanner de segredos, links e auditoria offline no `make validate`. Explicitar que
scanner e lockfile reduzem risco, mas não provam ausência absoluta de falhas.

## 4:40–6:20 — Demonstração local

Na raiz, em dois terminais:

```bash
# preparação (uma vez)
make install

# terminal 1: API
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# terminal 2: UI
npm --prefix frontend run dev -- --host 127.0.0.1
```

Sequência: (1) abrir a URL exibida pelo Vite; (2) autenticar no modo local; (3)
selecionar/cadastrar time; (4) pesquisar adversário; (5) abrir nova análise e
inspecionar fontes; (6) acionar **Analisar**; (7) percorrer grafo, vídeo, plano e
relatório; (8) confirmar health e executar a prova offline:

```bash
curl --fail http://127.0.0.1:8000/api/health
RUN_ONLINE_LLM_EXPERIMENTS=false python experiments/runners/run_offline.py
```

Usar dados locais na gravação; uma URL pública de vídeo pode falhar por rede,
restrição de idade, formato ou indisponibilidade e não deve bloquear a demo.

## 6:20–7:00 — Limitações e próximos passos

Registrar: provedores reais não foram validados; auditoria npm foi offline; não
há firewall de egress nem storage multi-instância no repositório; frontend tem
apenas teste contratual mínimo. Próximos passos: ambiente de staging com egress,
testes de navegador, auditoria CVE online, observabilidade e experimento humano
cego com dados licenciados.

Encerrar sem alegar gravação, deploy público ou resultado online.
