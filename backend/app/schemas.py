from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    club_name: str = Field(..., min_length=2, max_length=120)


class TacticalAnalysisResponse(BaseModel):
    id: int
    club_name: str
    formation: str
    strengths: list[str]
    weaknesses: list[str]
    key_players: list[str]
    recent_matches: list[str]
    game_plan: str
    simulation_note: str
    created_at: datetime

    model_config = {"from_attributes": True}
