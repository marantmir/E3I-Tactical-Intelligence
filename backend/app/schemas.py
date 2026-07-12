from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    team_id: int | None = None
    team_name: str = Field(min_length=1)
    competition: str = Field(min_length=1)
    season: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    user_profile: str = Field(min_length=1)


class OnlineTeamProfileSave(BaseModel):
    team_name: str = Field(min_length=1)
    country: str | None = None
    league: str | None = None
    coach: str | None = None
    base_formation: str | None = None
    style: str | None = None
    confidence: str | None = None
    status: str | None = None
    category: str | None = None
    online_search: dict = Field(default_factory=dict)


class ReportCreate(BaseModel):
    team_id: int
    objective: str = Field(default="Relatorio para comissao tecnica")
    user_profile: str = Field(default="Analista de desempenho")


class OwnTeamSet(BaseModel):
    ref: str = Field(min_length=1)
