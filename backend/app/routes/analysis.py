from fastapi import APIRouter

from ..database import create_analysis, list_history
from ..schemas import AnalysisCreate


router = APIRouter(tags=["analysis"])


@router.post("/api/analysis", status_code=201)
def create(payload: AnalysisCreate):
    return create_analysis(payload.model_dump())


@router.get("/api/history")
def history():
    return list_history()
