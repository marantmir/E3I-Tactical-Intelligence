"""Thin, validated adapters from the tool registry to tactical services.

This module intentionally contains no ranking, vision, graph, or optimisation
algorithm.  It only resolves bounded inputs, delegates to the existing service,
and attaches honest provenance metadata to the serialisable result.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from . import data_store
from .graph_analysis import build_tactical_graph
from .llm_assistant import analyze_video_tactics, analyze_video_visually
from .operational_research import build_operational_research
from .tactical_search.integration import search_tactical_enhanced


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TacticalSearchInput(StrictInput):
    team_name: str = Field(min_length=1, max_length=120)
    query: str | None = Field(default=None, min_length=1, max_length=500)
    max_sources: int = Field(default=8, ge=1, le=24)


class VisionInput(StrictInput):
    team_name: str = Field(min_length=1, max_length=120)
    vision_result: dict[str, Any]


class TeamInput(StrictInput):
    team_id: int = Field(gt=0, le=2_147_483_647)


class OperationalResearchInput(TeamInput):
    formation: str | None = Field(default=None, pattern=r"^\d(?:-\d){1,4}$", max_length=15)


def _result(*, service: str, nature: Literal["real", "heuristic", "simulated", "external_unavailable"],
            confidence: str, data: Any, limitations: list[str] | None = None) -> dict[str, Any]:
    return {
        "provenance": {"service": service, "nature": nature, "confidence": confidence},
        "data": data,
        "limitations": limitations or [],
    }


def search_tactical_information(value: TacticalSearchInput) -> dict[str, Any]:
    data = search_tactical_enhanced(
        value.team_name, value.query, value.max_sources,
        use_cache=True, use_llm_ranking=False, use_recency=True,
    )
    nature = "real" if data.get("sources") else "external_unavailable"
    return _result(
        service="tactical_search.integration.search_tactical_enhanced",
        nature=nature,
        confidence="source_dependent" if data.get("sources") else "unavailable",
        data=data,
        limitations=["Public sources may be incomplete or stale; verify claims against each source."],
    )


def extract_tactical_ocr(value: VisionInput) -> dict[str, Any]:
    data = analyze_video_visually(value.team_name, value.vision_result)
    return _result(
        service="llm_assistant.analyze_video_visually",
        nature="heuristic",
        confidence="model_or_local_fallback",
        data=data,
        limitations=["OCR is assisted visual interpretation, not confirmed transcription."],
    )


def analyze_video_frames(value: VisionInput) -> dict[str, Any]:
    data = analyze_video_tactics(value.team_name, value.vision_result)
    return _result(
        service="llm_assistant.analyze_video_tactics",
        nature="heuristic",
        confidence="derived_from_supplied_cv_observations",
        data=data,
        limitations=["Conclusions are hypotheses derived from the supplied frame observations."],
    )


def _team_records(team_id: int) -> tuple[dict, list[dict], list[dict]]:
    return (
        data_store.get_team(team_id),
        data_store.get_team_records(data_store.players(), team_id),
        data_store.get_team_records(data_store.formations(), team_id),
    )


def calculate_tactical_metrics(value: TeamInput) -> dict[str, Any]:
    team, players, formations = _team_records(value.team_id)
    graph = build_tactical_graph(team, players, formations)
    return _result(
        service="graph_analysis.build_tactical_graph",
        nature="heuristic",
        confidence="derived_from_registered_team_data",
        data={"metrics": graph["metrics"], "formation": graph["formation"]},
        limitations=["Metrics are projections from registered data, not match-event measurements."],
    )


def run_operational_research(value: OperationalResearchInput) -> dict[str, Any]:
    team, players, formations = _team_records(value.team_id)
    data = build_operational_research(team, players, formations, value.formation)
    return _result(
        service="operational_research.build_operational_research",
        nature="heuristic",
        confidence="exact_solver_over_registered_inputs",
        data=data,
        limitations=["The solver is exact for its model; its inputs and fit assumptions remain heuristic."],
    )


def get_team_context(value: TeamInput) -> dict[str, Any]:
    team, players, formations = _team_records(value.team_id)
    return _result(
        service="data_store.get_team/get_team_records",
        nature="real",
        confidence="registered_local_data",
        data={"team": team, "players": players, "formations": formations},
        limitations=["Context reflects the current local dataset and may not be current in the real world."],
    )
