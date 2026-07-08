from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TacticalAnalysis(Base):
    __tablename__ = "tactical_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_name: Mapped[str] = mapped_column(String(120), index=True)
    formation: Mapped[str] = mapped_column(String(30))
    strengths: Mapped[list[str]] = mapped_column(JSON)
    weaknesses: Mapped[list[str]] = mapped_column(JSON)
    key_players: Mapped[list[str]] = mapped_column(JSON)
    recent_matches: Mapped[list[str]] = mapped_column(JSON)
    game_plan: Mapped[str] = mapped_column(String(1000))
    simulation_note: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
