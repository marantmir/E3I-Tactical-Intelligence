from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TacticalAnalysis
from ..schemas import AnalysisCreate, TacticalAnalysisResponse
from ..services.mock_ai import generate_mock_analysis

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post(
    "",
    response_model=TacticalAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    profile = generate_mock_analysis(payload.club_name)
    analysis = TacticalAnalysis(
        club_name=payload.club_name.strip(),
        formation=profile.formation,
        strengths=profile.strengths,
        weaknesses=profile.weaknesses,
        key_players=profile.key_players,
        recent_matches=profile.recent_matches,
        game_plan=profile.game_plan,
        simulation_note=profile.simulation_note,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("", response_model=list[TacticalAnalysisResponse])
def list_analyses(db: Session = Depends(get_db)):
    return db.query(TacticalAnalysis).order_by(desc(TacticalAnalysis.created_at)).all()


@router.get("/{analysis_id}", response_model=TacticalAnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(TacticalAnalysis, analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    return analysis
