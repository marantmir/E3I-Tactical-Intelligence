from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    team_id: int | None = None
    team_name: str = Field(min_length=1)
    competition: str = Field(min_length=1)
    season: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    user_profile: str = Field(min_length=1)


class ReportCreate(BaseModel):
    team_id: int
    objective: str = Field(default="Relatorio para comissao tecnica")
    user_profile: str = Field(default="Analista de desempenho")
