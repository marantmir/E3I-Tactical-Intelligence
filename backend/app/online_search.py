from __future__ import annotations

import json
import urllib.parse
import urllib.request


USER_AGENT = "E3I-Tactical-Intelligence/0.1 academic prototype"


def _fetch_json(url: str, timeout: int = 5) -> dict | list:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def search_public_team_info(team_name: str) -> dict:
    """Best-effort public lookup. The product still works when the web is unavailable."""
    query = urllib.parse.quote(f"{team_name} futebol")
    search_url = (
        "https://pt.wikipedia.org/w/api.php"
        f"?action=opensearch&search={query}&limit=3&namespace=0&format=json"
    )

    try:
        result = _fetch_json(search_url)
        titles = result[1] if len(result) > 1 else []
        descriptions = result[2] if len(result) > 2 else []
        links = result[3] if len(result) > 3 else []

        sources = []
        for index, title in enumerate(titles):
            sources.append(
                {
                    "title": title,
                    "origin": "Wikipedia publica",
                    "url": links[index] if index < len(links) else "",
                    "summary": descriptions[index] if index < len(descriptions) else "",
                    "relevance": "Alta" if index == 0 else "Media",
                }
            )

        summary = sources[0]["summary"] if sources else ""
        if titles:
            page_title = urllib.parse.quote(titles[0].replace(" ", "_"))
            summary_url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{page_title}"
            try:
                page_summary = _fetch_json(summary_url)
                summary = page_summary.get("extract") or summary
            except Exception:
                pass

        return {
            "status": "available" if sources else "empty",
            "query": f"{team_name} futebol",
            "summary": summary or "Nenhum resumo publico foi encontrado para o termo pesquisado.",
            "sources": sources,
            "note": "Busca publica online sem uso de IA. Resultados devem ser revisados por analista humano.",
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "query": f"{team_name} futebol",
            "summary": "Busca online indisponivel no momento; pre-analise gerada com dados mockados.",
            "sources": [],
            "note": f"Falha de busca online tratada sem interromper o fluxo: {exc.__class__.__name__}.",
        }
