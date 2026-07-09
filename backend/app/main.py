from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import analysis, reports, teams


app = FastAPI(
    title="E3I Tactical Intelligence",
    description="API mockada para prototipo academico sem integracao real com IA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router)
app.include_router(analysis.router)
app.include_router(reports.router)

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "online",
        "service": "E3I Tactical Intelligence",
        "ai_integration": "disabled",
        "data_source": "mocked",
    }


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Frontend build nao encontrado. Execute npm run build em frontend/.",
        "api_docs": "/docs",
    }
