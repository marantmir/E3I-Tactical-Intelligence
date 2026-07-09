from fastapi import APIRouter, Query

from ..mock_store import (
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


router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("")
@router.get("/")
def list_teams():
    return teams()


@router.get("/search")
def search(query: str = Query(default="")):
    return search_teams(query)


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


@router.get("/{team_id}/game-plan")
def team_game_plan(team_id: int):
    return get_single_team_record(game_plans(), team_id, "Plano de jogo")
