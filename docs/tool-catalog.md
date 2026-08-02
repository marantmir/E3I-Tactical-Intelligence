# Catálogo de tools táticas

As tools são adaptadores finos: validam com Pydantic (`strict`, `extra=forbid`), chamam o serviço indicado e devolvem `provenance`, `data` e `limitations`. “Exato” descreve apenas o solver; não transforma dados ou premissas heurísticas em fatos.

| Tool | Finalidade | Input | Output | Timeout | Serviço reutilizado | Natureza |
|---|---|---|---|---:|---|---|
| `search_tactical_information` | Buscar fontes táticas públicas | `team_name`, `query?`, `max_sources` | fontes, estado e proveniência | 15 s | `search_tactical_enhanced` | real quando há fontes; indisponível sem fonte externa |
| `extract_tactical_ocr` | Interpretar texto visível nos quadros já fornecidos | `team_name`, `vision_result` | leitura visual e limitações | 12 s | `analyze_video_visually` | heurístico |
| `analyze_video_frames` | Sintetizar observações produzidas pelo pipeline de CV | `team_name`, `vision_result` | padrões e hipóteses | 12 s | `analyze_video_tactics` | heurístico |
| `calculate_tactical_metrics` | Projetar métricas de grafo do time local | `team_id` | métricas e formação | 5 s | `build_tactical_graph` | heurístico |
| `run_operational_research` | Otimizar escalação e comparar cenários | `team_id`, `formation?` | solução e comparação | 8 s | `build_operational_research` | heurístico; solver exato sobre premissas |
| `get_team_context` | Recuperar contexto cadastrado | `team_id` | time, elenco e formações | 3 s | `data_store` | real no conjunto local |

## Limitações e segurança

Nenhuma tool aceita URL ou caminho de arquivo; portanto a superfície atual não realiza download nem precisa resolver DNS/redirecionamentos. A busca delegada recebe texto e conserva os controles do serviço existente. Se futuramente uma URL entrar no schema, ela deverá ter HTTP(S), resolução e redirecionamentos revalidados contra loopback, redes privadas e link-local, além de allowlist quando possível, timeout e limite de bytes.

O registry aplica allowlist explícita, limite de entrada/saída, timeout e serialização JSON estrita. Erros do serviço viram mensagem genérica, sem stack trace, segredo, configuração ou caminho interno. OCR assistido e análises derivadas nunca são rotulados como confirmação factual. Dependências de rede, dados locais desatualizados e credenciais opcionais são declaradas no campo `limitations`.

## Fronteira de segurança comum

Somente nomes registrados na allowlist podem executar. Todos os argumentos passam por modelo Pydantic fechado e limites serializados; cada execução tem timeout e limite de resposta. Exceções inesperadas viram `Tool execution failed`, enquanto logs contêm tool, status e duração — não argumentos, resultados nem credenciais. Esses controles reduzem risco de prompt injection virar execução arbitrária; conteúdo retornado ainda deve ser tratado como dado não confiável.
