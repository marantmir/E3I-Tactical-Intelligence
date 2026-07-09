from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

from .data_store import find_team_by_name, get_team


DB_PATH = Path(__file__).resolve().parents[1] / "e3i_tactical.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                competition TEXT NOT NULL,
                season TEXT NOT NULL,
                objective TEXT NOT NULL,
                user_profile TEXT NOT NULL,
                base_formation TEXT NOT NULL,
                confidence TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM analysis_history").fetchone()[0]
        if count == 0:
            seed_history(connection)


def seed_history(connection: sqlite3.Connection) -> None:
    samples = [
        (1, "Analise de adversario", "Analista de desempenho", "Concluida"),
        (2, "Preparacao de jogo", "Treinador", "Concluida"),
        (6, "Relatorio para comissao tecnica", "Coordenador tecnico", "Em revisao"),
    ]
    now = datetime.now(timezone.utc).isoformat()
    for team_id, objective, user_profile, status in samples:
        team = get_team(team_id)
        connection.execute(
            """
            INSERT INTO analysis_history (
                team_id, team_name, competition, season, objective, user_profile,
                base_formation, confidence, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                team_id,
                team["name"],
                team["league"],
                "2026",
                objective,
                user_profile,
                team["base_formation"],
                team["confidence"],
                status,
                now,
            ),
        )


def create_analysis(payload: dict) -> dict:
    init_db()
    selected_team = None
    if payload.get("team_id") is not None:
        selected_team = get_team(int(payload["team_id"]))
    if selected_team is None:
        selected_team = find_team_by_name(payload["team_name"])
    if selected_team is None:
        raise HTTPException(
            status_code=422,
            detail="Time nao encontrado na base local. Gere uma pre-analise valida antes de salvar.",
        )

    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analysis_history (
                team_id, team_name, competition, season, objective, user_profile,
                base_formation, confidence, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                selected_team["id"],
                selected_team["name"],
                payload["competition"],
                payload["season"],
                payload["objective"],
                payload["user_profile"],
                selected_team["base_formation"],
                selected_team["confidence"],
                "Concluida",
                created_at,
            ),
        )
        record_id = cursor.lastrowid

    return {
        "id": record_id,
        "team_id": selected_team["id"],
        "team_name": selected_team["name"],
        "competition": payload["competition"],
        "season": payload["season"],
        "objective": payload["objective"],
        "user_profile": payload["user_profile"],
        "base_formation": selected_team["base_formation"],
        "confidence": selected_team["confidence"],
        "status": "Concluida",
        "created_at": created_at,
    }


def list_history() -> list[dict]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM analysis_history
            ORDER BY datetime(created_at) DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
