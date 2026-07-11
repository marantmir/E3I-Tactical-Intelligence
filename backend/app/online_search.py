from __future__ import annotations

from datetime import datetime, timezone
import html
import json
import re
import urllib.parse
import urllib.request

from .llm_assistant import enrich_team_search, tactical_search_queries
from .wikipedia_lookup import fetch_team_wikipedia_profile


USER_AGENT = "E3I-Tactical-Intelligence/0.3 tactical-video-intelligence"
TIMEOUT_SECONDS = 5
MAX_SOURCES = 24


def _fetch_text(url: str, timeout: int = TIMEOUT_SECONDS) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _fetch_json(url: str, timeout: int = TIMEOUT_SECONDS) -> dict | list:
    return json.loads(_fetch_text(url, timeout=timeout))


def search_public_team_info(team_name: str) -> dict:
    """Best-effort tactical source lookup.

    This intentionally avoids institutional team data. The goal is to find
    videos, tactical breakdowns and match-footage references that can feed the
    visual analysis pipeline.
    """
    cleaned_name = " ".join(team_name.strip().split())
    query_text = f"{cleaned_name} futebol analise tatica videos"
    errors: list[dict] = []
    sources: list[dict] = []

    search_queries = tactical_search_queries(cleaned_name)
    for item in search_queries:
        sources.extend(
            _try_collect(
                item["label"],
                lambda item=item: _duckduckgo_lookup(item["query"], item["category"]),
                errors,
            )
        )
    sources.extend(_guided_video_sources(cleaned_name))

    wikipedia = _try_collect_one("Wikipedia", lambda: fetch_team_wikipedia_profile(cleaned_name), errors)
    if wikipedia:
        sources.append(
            _source(
                title=wikipedia["title"],
                origin="Wikipedia",
                url=wikipedia.get("page_url") or "",
                summary=wikipedia["summary"],
                category="team_form",
                relevance="Alta",
            )
        )

    sources = _dedupe_sources(sources)[:MAX_SOURCES]
    source_groups = _group_sources(sources)
    coverage = {key: len(value) for key, value in source_groups.items()}
    live_count = sum(1 for source in sources if source.get("origin") not in {"Busca sugerida", "Pesquisa sugerida"})
    status = _status_from(live_count, errors)

    result = {
        "status": status,
        "query": query_text,
        "llm_query_plan": search_queries,
        "summary": _build_summary(cleaned_name, sources, coverage, live_count),
        "sources": sources,
        "source_groups": source_groups,
        "coverage": coverage,
        "analysis_focus": _analysis_focus(cleaned_name, source_groups),
        "collection_plan": _collection_plan(cleaned_name),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors[:6],
        "note": _build_note(status, live_count, errors),
        "wikipedia": wikipedia,
        "crest_url": wikipedia.get("crest_url") if wikipedia else None,
    }
    result["llm_search"] = enrich_team_search(cleaned_name, result)
    return result


def _try_collect(label: str, collect, errors: list[dict]) -> list[dict]:
    try:
        return collect()
    except Exception as error:
        errors.append({"source": label, "error": error.__class__.__name__})
        return []


def _try_collect_one(label: str, collect, errors: list[dict]):
    try:
        return collect()
    except Exception as error:
        errors.append({"source": label, "error": error.__class__.__name__})
        return None


def _duckduckgo_lookup(query: str, category: str) -> list[dict]:
    encoded = urllib.parse.quote(query)
    text = _fetch_text(f"https://duckduckgo.com/html/?q={encoded}")
    sources = []
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        href = html.unescape(match.group("href"))
        title = _clean_text(_strip_tags(match.group("title")))
        url = _unwrap_duckduckgo_url(href)
        if not title or not url:
            continue
        sources.append(
            _source(
                title=title,
                origin="Busca web publica",
                url=url,
                summary=f"Referencia publica para revisar padroes taticos e material visual: {query}",
                category=category,
                relevance="Media",
            )
        )
        if len(sources) >= 6:
            break
    return sources


def _guided_video_sources(team_name: str) -> list[dict]:
    searches = [
        (
            "match_videos",
            "YouTube melhores momentos",
            "Videos de jogo e melhores momentos",
            "youtube.com/results",
            f"{team_name} futebol melhores momentos jogo completo analise",
            "Alta",
        ),
        (
            "analysis_videos",
            "YouTube analise tatica",
            "Analises taticas e comentarios sobre o modelo de jogo",
            "youtube.com/results",
            f"{team_name} analise tatica como joga",
            "Alta",
        ),
        (
            "team_form",
            "Busca web tatica",
            "Padroes de jogo e comportamento coletivo",
            "google.com/search",
            f"{team_name} futebol padroes taticos saida de bola pressao transicao",
            "Media",
        ),
    ]
    sources = []
    for category, origin, title, domain, query, relevance in searches:
        sources.append(
            _source(
                title=f"{title}: {team_name}",
                origin="Busca sugerida",
                url=_search_url(domain, query),
                summary=(
                    "Consulta estruturada para coletar material visual e tatico quando a busca direta "
                    "do ambiente estiver bloqueada ou incompleta."
                ),
                category=category,
                relevance=relevance,
            )
        )
    return sources


def _search_url(domain: str, query: str) -> str:
    encoded = urllib.parse.quote(query)
    if domain == "youtube.com/results":
        return f"https://www.youtube.com/results?search_query={encoded}"
    return f"https://www.google.com/search?q={encoded}"


def _source(
    *,
    title: str,
    origin: str,
    url: str,
    summary: str,
    category: str,
    relevance: str,
    published_at: str = "",
) -> dict:
    return {
        "title": title,
        "origin": origin,
        "url": url,
        "summary": summary,
        "category": category,
        "relevance": relevance,
        "published_at": published_at,
    }


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for source in sources:
        key = (source.get("url") or source.get("title") or "").strip().casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(source)
    return deduped


def _group_sources(sources: list[dict]) -> dict[str, list[dict]]:
    groups = {
        "match_videos": [],
        "analysis_videos": [],
        "team_form": [],
    }
    for source in sources:
        groups.setdefault(source.get("category") or "team_form", []).append(source)
    return groups


def _status_from(live_count: int, errors: list[dict]) -> str:
    if live_count > 0 and errors:
        return "partial"
    if live_count > 0:
        return "available"
    return "guided_fallback"


def _build_summary(team_name: str, sources: list[dict], coverage: dict, live_count: int) -> str:
    if live_count:
        return (
            f"Coleta tatica para {team_name}: {len(sources)} referencias organizadas, "
            f"incluindo {coverage.get('match_videos', 0)} referencias de video, "
            f"{coverage.get('analysis_videos', 0)} analises taticas e "
            f"{coverage.get('team_form', 0)} fontes sobre padroes de jogo."
        )
    return (
        f"A busca direta nao retornou fontes ao vivo neste ambiente. Mesmo assim, o dossie de {team_name} "
        "foi preparado com consultas estruturadas para videos de jogos e analises taticas."
    )


def _analysis_focus(team_name: str, groups: dict[str, list[dict]]) -> list[str]:
    focus = [
        f"Comparar videos de {team_name} para separar posse, pressao, transicoes e ultimo terco.",
        "Separar videos por jogo: saida de bola, pressao, transicoes, bola parada e ultimo terco.",
        "Priorizar trechos com camera aberta para melhorar tracking, homografia e leitura coletiva.",
    ]
    if groups.get("analysis_videos"):
        focus.append("Priorizar videos de analise tatica para validar padroes observados no rastreamento.")
    return focus


def _collection_plan(team_name: str) -> list[dict]:
    return [
        {
            "stage": "Videos de jogos",
            "action": f"Coletar melhores momentos e jogos completos recentes de {team_name}.",
        },
        {
            "stage": "Recortes taticos",
            "action": "Separar trechos de ataque posicional, transicao, pressao e bola parada.",
        },
        {
            "stage": "Analise visual",
            "action": "Subir os videos no painel para extrair trilhas, heatmap, conexoes e eventos taticos.",
        },
        {
            "stage": "Decisao",
            "action": "Combinar grafo, visao computacional e explicacao tatica do video.",
        },
    ]


def _build_note(status: str, live_count: int, errors: list[dict]) -> str:
    if status == "available":
        return "Busca publica restrita a material tatico e videos analisaveis."
    if status == "partial":
        failed = ", ".join(error["source"] for error in errors[:3])
        return f"Busca tatica parcial: {live_count} fonte(s) ao vivo; falhas tratadas em {failed}."
    return "Busca direta bloqueada ou sem resposta; links estruturados foram gerados para coleta manual."


def _unwrap_duckduckgo_url(url: str) -> str:
    if "uddg=" not in url:
        return url
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    return params.get("uddg", [url])[0]


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "")


def _clean_text(value: str) -> str:
    return " ".join(html.unescape(value or "").split())
