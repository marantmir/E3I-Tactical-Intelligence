# Checklist da Avaliacao

## Endpoint Funcional

- [x] Backend FastAPI responde em `/api/health`.
- [x] Frontend React pode ser servido pelo build de producao.
- [x] Rotas de API funcionam com modo local quando a rede externa falha.
- [x] Dockerfile incluido para deploy.
- [ ] Inserir link publico apos publicacao.

## Complexidade e Ambicao

- [x] Problema real de analise tatica.
- [x] Mais de 5 telas navegaveis.
- [x] Busca local e publica por time.
- [x] Botao `Analisar` antes de salvar.
- [x] Pre-analise com fontes, grafo, visao computacional e pesquisa operacional.
- [x] Grafo visual de conexoes taticas.
- [x] Mapa visual de videos com calor, trilhas e eventos.
- [x] Plano de jogo e relatorio final.
- [x] Historico persistido em SQLite.
- [x] Nao e chatbot simples.

## GitHub

- [x] Estrutura clara de pastas.
- [x] `.gitignore` adequado.
- [x] README atualizado.
- [x] Pasta `docs`.
- [x] Repositorio Git local inicializado em `main`.
- [x] Remote `origin` configurado.
- [ ] Fazer push para o GitHub.

## Validacao Tecnica

- [x] Pytest executável da raiz sem `PYTHONPATH` manual (405 testes).
- [x] Dependências de desenvolvimento incluem `pytest` e `httpx`.
- [x] Teste baseline, lint e build do frontend possuem scripts oficiais.
- [x] CI executa instalação, testes, compileall, build e lint em Python 3.12/Node 22.
- [x] Registro seguro de tools independente de provedor, com allowlist, validacao, timeout e limites de tamanho.
- [x] Testes unitarios do nucleo de tools sem chamadas externas.
- [x] Endpoints novos: `graph-analysis`, `video-vision`, `public-intelligence`.
- [x] Frontend consome as novas rotas.
- [x] Build Vite validado.
- [x] Code-splitting por rota (`React.lazy`/`Suspense`) no frontend.
- [x] CORS do FastAPI restrito por `ALLOWED_ORIGINS` (nao mais `*`).
- [x] Rate limiting nas rotas de upload de video (429 + `Retry-After`).
- [x] Logging estruturado em JSON com `request_id`/`X-Request-ID`.
- [x] Suite `pytest` cobrindo `graph_analysis`, `video_vision`, rate limiting, logging e rotas de `teams`/`analysis`.
- [x] Fluxo analisado no navegador local.
- [ ] Validar console no endpoint publicado.

## Experimento LLM reproduzível

Use o mesmo vídeo, `visual_key_frames` e JSON de métricas em todas as execuções. Não misture partidas nem altere prompt entre células. Execute cada célula três vezes e preserve as respostas (sem chaves) em um artefato datado.

| Execução | Provedor/modelo | Temperatura | Top P | JSON válido | Afirmações sustentadas / total | Alucinações | Latência (ms) | Tokens/custo |
|---|---|---:|---:|---|---:|---:|---:|---:|
| A1–A3 | modelo sob teste | 0,2 | 0,9 |  |  |  |  |  |
| B1–B3 | mesmo modelo | 0,0 | 0,9 |  |  |  |  |  |
| C1–C3 | modelo alternativo | 0,2 | 0,9 |  |  |  |  |  |

### Rubrica (0–2 por item)

1. **Grounding:** cada afirmação aponta para quadro, evento ou métrica fornecida.
2. **Calibração:** incerteza aumenta quando há poucos rastros/bola ausente.
3. **Utilidade tática:** próxima ação é verificável pela comissão técnica.
4. **Contrato:** JSON válido e campos esperados, sem prosa externa.
5. **Segurança factual:** nenhum nome, número, placar ou jogada sem evidência.

Antes de comparar modelos, defina o limiar: zero alucinações graves, JSON válido em 3/3 e pelo menos 8/10 na rubrica. Registre indisponibilidade de rede como “não executado”, nunca como resultado de qualidade. Esta tabela é um protocolo; o repositório não declara vencedor sem execuções reais e custos auditáveis.

## Núcleo de tool calling — Prompt 2

- [x] Fluxo completo offline com o mesmo modelo mock antes e depois da tool.
- [x] `get_llm_status` executada exclusivamente pelo `ToolRegistry`.
- [x] Chamadas/resultados normalizados e correlacionados por `tool_call_id`.
- [x] Histórico preservado e duas chamadas sequenciais cobertas.
- [x] Limite padrão 4 e configuração restrita a 1–8.
- [x] Tool desconhecida, argumentos inválidos/grandes, timeout e resultado grande tratados.
- [x] Erro interno sanitizado e logs sem argumentos integrais.
- [x] Ausência de credencial e falha do modelo usam fluxo seguro/fallback determinístico.
- [ ] Implementar adaptadores nativos de tool calling para os quatro provedores.
- [x] Registrar as seis tools táticas mínimas e o catálogo de proveniência.
- [x] Validar schema estrito, limites, timeout, falha sanitizada e JSON para cada tool.
- [x] Provar duas tools táticas sequenciais e preservação do primeiro resultado.
- [ ] Implementar adapters nativos de wire protocol para os quatro provedores.

## Tool calling multiprovedor

- [x] Texto, multimodal, tools, chamadas, resultados e resposta final nos quatro adaptadores.
- [x] Parâmetros compatíveis enviados e incompatíveis omitidos.
- [x] Ausência de credencial não inicia transporte.
- [x] Timeout/rate limit/temporário têm retry limitado; erros não transitórios não têm retry.
- [x] Fallback entre mocks, limite de tentativas, contexto preservado e fallback local.
- [x] Nenhuma chamada paga; validação online dos provedores: não executada.
