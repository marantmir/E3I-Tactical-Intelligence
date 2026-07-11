from app import online_search


def _stub_wikipedia_profile(**overrides):
    profile = {
        "title": "Flamengo",
        "description": "Clube de futebol brasileiro",
        "summary": "Resumo do Flamengo vindo da Wikipedia.",
        "crest_url": "https://upload.wikimedia.org/flamengo-crest.png",
        "page_url": "https://pt.wikipedia.org/wiki/Flamengo",
        "lang": "pt",
    }
    profile.update(overrides)
    return profile


def test_search_public_team_info_includes_wikipedia_profile(monkeypatch):
    monkeypatch.setattr(online_search, "_duckduckgo_lookup", lambda query, category: [])
    monkeypatch.setattr(online_search, "fetch_team_wikipedia_profile", lambda name: _stub_wikipedia_profile())

    result = online_search.search_public_team_info("Flamengo")

    assert result["crest_url"] == "https://upload.wikimedia.org/flamengo-crest.png"
    assert result["wikipedia"]["title"] == "Flamengo"
    wikipedia_sources = [source for source in result["sources"] if source["origin"] == "Wikipedia"]
    assert len(wikipedia_sources) == 1
    assert wikipedia_sources[0]["url"] == "https://pt.wikipedia.org/wiki/Flamengo"


def test_search_public_team_info_handles_missing_wikipedia_profile(monkeypatch):
    monkeypatch.setattr(online_search, "_duckduckgo_lookup", lambda query, category: [])
    monkeypatch.setattr(online_search, "fetch_team_wikipedia_profile", lambda name: None)

    result = online_search.search_public_team_info("Time Totalmente Inexistente")

    assert result["crest_url"] is None
    assert result["wikipedia"] is None
    assert not any(source["origin"] == "Wikipedia" for source in result["sources"])


def test_search_public_team_info_survives_wikipedia_lookup_raising(monkeypatch):
    def boom(name):
        raise RuntimeError("network blocked")

    monkeypatch.setattr(online_search, "_duckduckgo_lookup", lambda query, category: [])
    monkeypatch.setattr(online_search, "fetch_team_wikipedia_profile", boom)

    result = online_search.search_public_team_info("Flamengo")

    assert result["crest_url"] is None
    assert any(error["source"] == "Wikipedia" for error in result["errors"])
