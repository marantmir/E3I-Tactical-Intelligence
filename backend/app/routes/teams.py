from fastapi import APIRouter, Query

from ..graph_analysis import build_tactical_graph
from ..data_store import (
    formations,
    game_plans,
    get_single_team_record,
    get_team,
    get_team_records,
    players,
    search_teams,
    sources,
    tactical_analysis,
    teams,
)
from ..online_search import search_public_team_info
from ..video_vision import build_video_vision


router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("")
@router.get("/")
def list_teams():
    return teams()


@router.get("/search")
def search(query: str = Query(default="")):
    local_results = search_teams(query)
    if query.strip() and not local_results:
        online = search_public_team_info(query)
        return [
            {
                "id": 0,
                "name": query.strip(),
                "country": "A confirmar",
                "league": "Fonte publica",
                "coach": "A confirmar em fonte publica",
                "base_formation": "A definir",
                "style": online["summary"],
                "confidence": "Medio",
                "status": "Perfil online para pre-analise",
                "online_search": online,
            }
        ]
    return local_results


@router.get("/{team_id}")
def detail(team_id: int):
    return get_team(team_id)


@router.get("/{team_id}/tactical-analysis")
def team_tactical_analysis(team_id: int):
    return get_single_team_record(tactical_analysis(), team_id, "Dossie tatico")


@router.get("/{team_id}/formations")
def team_formations(team_id: int):
    return get_team_records(formations(), team_id)


@router.get("/{team_id}/players")
def team_players(team_id: int):
    return get_team_records(players(), team_id)


@router.get("/{team_id}/sources")
def team_sources(team_id: int):
    return get_team_records(sources(), team_id)


@router.get("/{team_id}/graph-analysis")
def team_graph_analysis(team_id: int):
    team = get_team(team_id)
    return build_tactical_graph(team, get_team_records(players(), team_id), get_team_records(formations(), team_id))


@router.get("/{team_id}/video-vision")
def team_video_vision(team_id: int):
    team = get_team(team_id)
    return build_video_vision(team, get_team_records(sources(), team_id))


@router.get("/{team_id}/public-intelligence")
def team_public_intelligence(team_id: int):
    team = get_team(team_id)
    return search_public_team_info(team["name"])


@router.get("/{team_id}/game-plan")
def team_game_plan(team_id: int):
    return get_single_team_record(game_plans(), team_id, "Plano de jogo")
