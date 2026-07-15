"""Tactical Search Hub: Sistema de busca tática integrado para futebol.

Pipeline completo de busca com cache, retry, paralelização, LLM e scoring temporal:

Fluxo:
1. Normalizar query + detectar formação + idioma
2. Check cache (Redis/SQLite com TTL 7 dias)
3. Se miss → buscar em paralelo (web, YouTube, Wikipedia)
4. Aplicar retry exponencial com jitter em falhas
5. Validar qualidade de vídeos (duração, resolução)
6. Ranking tático (palavras-chave + formação + autoridade)
7. Enriquecimento semântico via LLM (se disponível)
8. Scoring de recência (tendência de views, autoridade, temporal)
9. Dedupe + cache + return ranked sources

Componentes:
- cache_layer.py: Cache abstrato com fallback chain
- tactical_keywords.py: 200+ keywords em 3 idiomas + formação
- video_validator.py: Parse de duração, resolução, qualidade
- tactical_ranking.py: Ranking baseado em relevância tática
- retry_policy.py: Exponential backoff com jitter
- parallel_search.py: Executor paralelo com timeout
- llm_tactical_enrichment.py: Query enrichment + re-ranking semântico
- recency_scoring.py: Trending + autoridade + decay temporal
- search_hub.py: Orquestrador central

Requisitos:
- Python 3.11+
- redis (opcional, fallback para SQLite/Memory)
- urllib.request (built-in)

Exemplo de uso:

    from backend.app.tactical_search.search_hub import tactical_search

    result = tactical_search("Flamengo 4-3-3 pressão alta", max_sources=24)

    # result = {
    #     "query": "Flamengo 4-3-3 pressão alta",
    #     "formation": "4-3-3",
    #     "cached": False,
    #     "sources": [
    #         {
    #             "title": "...",
    #             "url": "...",
    #             "score": 8.5,
    #             "category": "analysis_videos",
    #             "tactical_score": 8.2,
    #             "recency_score": 7.8,
    #             "combined_score": 8.1,
    #             ...
    #         },
    #         ...
    #     ],
    #     "summary": "Coleta tática: 12 fontes (8 analysis_videos, 4 match_videos)",
    #     "status": "available",
    #     "errors": []
    # }
"""
from .search_hub import tactical_search

__all__ = ["tactical_search"]
__version__ = "2.4.0"
