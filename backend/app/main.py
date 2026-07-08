from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers.analyses import router as analyses_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E3I Tactical Intelligence API",
    description="Mocked tactical football intelligence prototype.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyses_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "E3I Tactical Intelligence API"}
