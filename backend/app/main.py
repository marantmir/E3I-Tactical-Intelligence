import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import analysis, llm, reports, teams


app = FastAPI(
    title="E3I Tactical Intelligence",
    description="API para inteligencia tatica com busca publica, grafos e leitura visual de videos.",
    version="0.1.0",
)

DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(llm.router)

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "online",
        "service": "E3I Tactical Intelligence",
        "ai_integration": "evidence_assisted",
        "data_source": "public_and_local",
    }


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/logo-e3i.png", include_in_schema=False)
def serve_logo():
    logo_file = FRONTEND_DIST / "logo-e3i.png"
    if logo_file.exists():
        return FileResponse(logo_file)
    return {"message": "Logo nao encontrado no build do frontend."}


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Frontend build nao encontrado. Execute npm run build em frontend/.",
        "api_docs": "/docs",
    }
