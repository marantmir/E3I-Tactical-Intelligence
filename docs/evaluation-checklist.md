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
