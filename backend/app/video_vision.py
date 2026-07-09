from __future__ import annotations


def build_video_vision(team: dict, sources: list[dict]) -> dict:
    video_sources = [source for source in sources if source["type"].casefold() == "video"]
    if not video_sources:
        video_sources = sources[:2]

    frames = []
    heatmap = []
    movement_tracks = []
    events = []

    for index, source in enumerate(video_sources[:4]):
        base_x = 20 + index * 16
        base_y = 72 - index * 10
        frames.append(
            {
                "id": f"frame-{index + 1}",
                "time": f"{8 + index * 11}:00",
                "title": source["title"],
                "focus": _focus_from_summary(source["summary"]),
                "confidence": source["relevance"],
            }
        )
        heatmap.append({"x": min(82, base_x + 8), "y": max(16, base_y), "intensity": 66 + index * 8})
        heatmap.append({"x": min(88, base_x + 20), "y": max(18, base_y - 14), "intensity": 52 + index * 7})
        movement_tracks.append(
            {
                "label": _focus_from_summary(source["summary"]),
                "points": [
                    {"x": base_x, "y": base_y},
                    {"x": base_x + 14, "y": base_y - 10},
                    {"x": base_x + 28, "y": base_y - 18},
                ],
            }
        )
        events.append(
            {
                "minute": 8 + index * 11,
                "event": source["title"],
                "finding": source["summary"],
                "recommendation": _recommendation_from_summary(source["summary"]),
            }
        )

    return {
        "team": team["name"],
        "status": "ready",
        "frames": frames,
        "heatmap": heatmap,
        "movement_tracks": movement_tracks,
        "events": events,
        "summary": (
            "Leitura visual preparada para revisar ocupacao de espaco, corredores de progressao, "
            "compactacao e gatilhos de pressao a partir dos videos e fontes anexadas."
        ),
    }


def _focus_from_summary(summary: str) -> str:
    normalized = summary.casefold()
    if "segundo pau" in normalized or "cruzamento" in normalized:
        return "Ataque ao segundo pau"
    if "pressao" in normalized or "recuperacao" in normalized:
        return "Gatilho de pressao"
    if "corredor" in normalized or "lateral" in normalized:
        return "Progressao lateral"
    if "profundidade" in normalized or "costas" in normalized:
        return "Ataque a profundidade"
    if "posse" in normalized or "passe" in normalized:
        return "Circulacao e apoios"
    return "Padrao coletivo"


def _recommendation_from_summary(summary: str) -> str:
    normalized = summary.casefold()
    if "vulnerabilidade" in normalized or "espaco" in normalized:
        return "Treinar cobertura e temporizacao na zona vulneravel."
    if "bola parada" in normalized or "escanteio" in normalized:
        return "Separar bloco de treino para bloqueios, marcacao e segunda bola."
    if "pressao" in normalized or "recuperacao" in normalized:
        return "Ensaiar saida sob pressao e passe de escape no lado oposto."
    if "amplitude" in normalized or "corredor" in normalized:
        return "Controlar largura defensiva e orientar o adversario para zona de menor risco."
    return "Revisar o lance com a comissao e vincular ao plano de jogo."
