"""Pesquisa operacional aplicada ao plano de jogo.

Este modulo entrega a camada de otimizacao prometida pelo produto:

1. Escalacao otima (problema de atribuicao): cada jogador do elenco e cada
   vaga da formacao viram nos de um grafo bipartido; o peso da aresta e o
   "fit" do jogador na vaga (afinidade posicional x nota tatica + bonus de
   influencia/status). A escalacao que maximiza a soma dos fits e resolvida
   com `networkx.max_weight_matching` (algoritmo blossom, exato, sem
   dependencia extra) - nao com heuristica gulosa, que erra quando um
   jogador serve bem em duas vagas.

2. Comparacao de cenarios: cada formacao conhecida do time e otimizada e
   recebe indices ofensivo/defensivo/equilibrio derivados da escalacao
   otima, gerando recomendacoes por estado de jogo (vencendo, empatando,
   perdendo).

Tudo e deterministico e explicavel: cada atribuicao carrega afinidade, nota
e justificativa, para que a comissao tecnica audite a sugestao em vez de
receber um numero opaco.
"""
from __future__ import annotations

import re

import networkx as nx


# Afinidade entre a posicao de origem do jogador e a posicao da vaga.
# 1.0 = posicao natural; valores parciais refletem adaptacoes comuns no
# futebol (ex.: volante improvisado de zagueiro). Pares ausentes recebem
# CROSS_AFFINITY; linha no gol (e vice-versa) recebe GOAL_MISMATCH.
POSITION_AFFINITY: dict[str, dict[str, float]] = {
    "GOL": {"GOL": 1.0},
    "ZAG": {"ZAG": 1.0, "LAT": 0.55, "VOL": 0.5},
    "LAT": {"LAT": 1.0, "ZAG": 0.5, "MEI": 0.45, "ATA": 0.35},
    "VOL": {"VOL": 1.0, "ZAG": 0.5, "MEI": 0.65},
    "MEI": {"MEI": 1.0, "VOL": 0.6, "ATA": 0.6},
    "ATA": {"ATA": 1.0, "MEI": 0.55, "LAT": 0.3},
}
CROSS_AFFINITY = 0.15
GOAL_MISMATCH = 0.02
DEFENSIVE_SLOTS = {"GOL", "ZAG", "LAT", "VOL"}
OFFENSIVE_SLOTS = {"MEI", "ATA"}
INFLUENCE_BONUS = {"Alta": 0.4, "Media": 0.15}
STARTER_BONUS = 0.25
GAME_STATES = ("vencendo", "empatando", "perdendo")


def parse_formation_slots(formation: str) -> list[dict]:
    """Converte "4-2-3-1" em vagas posicionais (GOL + linhas).

    Regras: primeira linha e a defesa (4+ jogadores = 2 laterais + zagueiros;
    3 ou menos = so zagueiros), a ultima linha e o ataque, linhas
    intermediarias comecam na base (volantes) e sobem para criacao (meias).
    Uma unica linha intermediaria e dividida entre base e criacao.
    """
    numbers = [int(part) for part in re.findall(r"\d+", formation or "") if 0 < int(part) <= 6]
    if len(numbers) < 2:
        numbers = [4, 3, 3]

    slots: list[dict] = [{"slot_id": 0, "position": "GOL", "line": "gol"}]
    slot_id = 1

    def add(position: str, line: str, count: int) -> None:
        nonlocal slot_id
        for _ in range(count):
            slots.append({"slot_id": slot_id, "position": position, "line": line})
            slot_id += 1

    defense, *middles, attack = numbers
    if defense >= 4:
        add("LAT", "defesa", 2)
        add("ZAG", "defesa", defense - 2)
    else:
        add("ZAG", "defesa", defense)

    if len(middles) == 1:
        base = middles[0] // 2
        add("VOL", "meio", base)
        add("MEI", "meio", middles[0] - base)
    elif middles:
        add("VOL", "meio", middles[0])
        for row in middles[1:]:
            add("MEI", "meio", row)

    add("ATA", "ataque", attack)
    return slots


def _slot_affinity(player_position: str, slot_position: str) -> float:
    origin = (player_position or "").strip().upper()
    if origin == slot_position:
        return 1.0
    if "GOL" in (origin, slot_position):
        return POSITION_AFFINITY.get(origin, {}).get(slot_position, GOAL_MISMATCH)
    return POSITION_AFFINITY.get(origin, {}).get(slot_position, CROSS_AFFINITY)


def _fit_score(player: dict, slot_position: str) -> float:
    """Fit 0-10: afinidade posicional escala a nota tatica, com bonus leve de
    influencia e status de titular. O bonus nunca supera a afinidade para nao
    escalar um atacante no gol so porque ele e influente."""
    affinity = _slot_affinity(player.get("position", ""), slot_position)
    base = float(player.get("tactical_score") or 0.0)
    bonus = INFLUENCE_BONUS.get(str(player.get("influence") or ""), 0.0)
    if str(player.get("status") or "").strip().casefold() == "titular":
        bonus += STARTER_BONUS
    return round(min(10.0, affinity * base + affinity * bonus), 2)


def optimize_lineup(players: list[dict], formation: str) -> dict:
    """Resolve o problema de atribuicao jogador->vaga de forma exata."""
    slots = parse_formation_slots(formation)
    if not players:
        return {
            "status": "sem_elenco",
            "formation": formation,
            "slots": slots,
            "assignments": [],
            "bench": [],
            "lineup_strength": 0.0,
            "positional_coverage": 0.0,
            "gaps": [slot["position"] for slot in slots],
            "note": "Cadastre o elenco (Administracao > Elenco) para otimizar a escalacao.",
        }

    graph = nx.Graph()
    for index, player in enumerate(players):
        graph.add_node(("p", index))
    for slot in slots:
        graph.add_node(("s", slot["slot_id"]))
    for index, player in enumerate(players):
        for slot in slots:
            weight = _fit_score(player, slot["position"])
            if weight > 0:
                graph.add_edge(("p", index), ("s", slot["slot_id"]), weight=weight)

    matching = nx.max_weight_matching(graph, maxcardinality=True)
    slot_to_player: dict[int, int] = {}
    for left, right in matching:
        if left[0] == "s":
            left, right = right, left
        slot_to_player[right[1]] = left[1]

    assignments = []
    used_players: set[int] = set()
    for slot in slots:
        player_index = slot_to_player.get(slot["slot_id"])
        if player_index is None:
            assignments.append(
                {
                    **slot,
                    "player": None,
                    "fit": 0.0,
                    "natural_position": False,
                    "explanation": "Sem jogador disponivel para esta vaga no elenco cadastrado.",
                }
            )
            continue
        used_players.add(player_index)
        player = players[player_index]
        fit = _fit_score(player, slot["position"])
        natural = (player.get("position", "").strip().upper() == slot["position"])
        assignments.append(
            {
                **slot,
                "player": {
                    "id": player.get("id"),
                    "name": player.get("name"),
                    "position": player.get("position"),
                    "tactical_score": player.get("tactical_score"),
                    "influence": player.get("influence"),
                    "risk_level": player.get("risk_level"),
                    "status": player.get("status"),
                },
                "fit": fit,
                "natural_position": natural,
                "explanation": (
                    "Posicao natural."
                    if natural
                    else f"Adaptado de {player.get('position') or 'posicao nao informada'} "
                    f"(afinidade {_slot_affinity(player.get('position', ''), slot['position']):.2f})."
                ),
            }
        )

    bench = sorted(
        (
            {
                "id": player.get("id"),
                "name": player.get("name"),
                "position": player.get("position"),
                "tactical_score": player.get("tactical_score"),
            }
            for index, player in enumerate(players)
            if index not in used_players
        ),
        key=lambda item: float(item.get("tactical_score") or 0.0),
        reverse=True,
    )

    filled = [item for item in assignments if item["player"] is not None]
    strength = round(sum(item["fit"] for item in filled) / max(1, len(slots)), 2)
    gaps = [item["position"] for item in assignments if item["player"] is None or item["fit"] < 4.0]

    return {
        "status": "otimizado",
        "formation": formation,
        "method": "matching_bipartido_peso_maximo_exato",
        "assignments": assignments,
        "bench": bench,
        "lineup_strength": strength,
        "positional_coverage": round(len(filled) / max(1, len(slots)) * 100, 1),
        "gaps": gaps,
        "note": (
            "Escalacao que maximiza a soma dos fits jogador-vaga. Fits baixos e vagas sem "
            "jogador indicam onde o elenco cadastrado nao cobre a formacao."
        ),
    }


def _line_index(assignments: list[dict], slot_positions: set[str]) -> float:
    fits = [item["fit"] for item in assignments if item["position"] in slot_positions]
    return round(sum(fits) / max(1, len(fits)), 2)


def compare_formation_scenarios(players: list[dict], formations: list[dict]) -> dict:
    """Otimiza cada formacao conhecida e recomenda uma por estado de jogo."""
    scenarios = []
    for record in formations:
        lineup = optimize_lineup(players, record.get("formation") or "")
        offensive = _line_index(lineup["assignments"], OFFENSIVE_SLOTS)
        defensive = _line_index(lineup["assignments"], DEFENSIVE_SLOTS)
        balance = round(10.0 - abs(offensive - defensive), 2)
        probability = float(record.get("probability") or 0)
        scenarios.append(
            {
                "formation": record.get("formation"),
                "context": record.get("context") or "",
                "probability": probability,
                "lineup_strength": lineup["lineup_strength"],
                "offensive_index": offensive,
                "defensive_index": defensive,
                "balance_index": balance,
                "gaps": lineup["gaps"],
                # Utilidade combina qualidade da escalacao otima com a
                # aderencia observada da formacao ao contexto do time.
                "utility": round(0.65 * lineup["lineup_strength"] + 0.35 * probability / 10, 2),
                "risks": record.get("risks") or "",
            }
        )

    scenarios.sort(key=lambda item: item["utility"], reverse=True)

    recommendations = {}
    if scenarios:
        by_defense = max(scenarios, key=lambda item: (item["defensive_index"], item["utility"]))
        by_attack = max(scenarios, key=lambda item: (item["offensive_index"], item["utility"]))
        by_balance = max(scenarios, key=lambda item: (item["balance_index"], item["utility"]))
        recommendations = {
            "vencendo": {
                "formation": by_defense["formation"],
                "reason": f"Maior indice defensivo otimizado ({by_defense['defensive_index']}).",
            },
            "empatando": {
                "formation": by_balance["formation"],
                "reason": f"Melhor equilibrio entre linhas ({by_balance['balance_index']}).",
            },
            "perdendo": {
                "formation": by_attack["formation"],
                "reason": f"Maior indice ofensivo otimizado ({by_attack['offensive_index']}).",
            },
        }

    return {
        "scenarios": scenarios,
        "recommendations": recommendations,
        "note": (
            "Indices derivados da escalacao otima de cada formacao com o elenco cadastrado. "
            "Recomendacoes por estado de jogo sao ponto de partida para a comissao, nao decisao final."
        ),
    }


def build_operational_research(
    team: dict,
    players: list[dict],
    formations: list[dict],
    requested_formation: str | None = None,
) -> dict:
    candidates = list(formations)
    if not candidates and team.get("base_formation"):
        candidates = [
            {
                "formation": team["base_formation"],
                "probability": 50,
                "context": "Formacao base cadastrada do time (sem alternativas coletadas).",
                "risks": "",
            }
        ]

    comparison = compare_formation_scenarios(players, candidates)
    target_formation = (
        requested_formation
        or (comparison["scenarios"][0]["formation"] if comparison["scenarios"] else None)
        or team.get("base_formation")
        or "4-3-3"
    )
    lineup = optimize_lineup(players, target_formation)

    return {
        "team": team.get("name"),
        "method": {
            "model": "problema_de_atribuicao",
            "solver": "networkx.max_weight_matching (blossom, exato)",
            "objective": "maximizar soma dos fits jogador-vaga da formacao",
        },
        "target_formation": target_formation,
        "lineup": lineup,
        "formation_comparison": comparison,
        "squad_size": len(players),
    }
