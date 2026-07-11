from __future__ import annotations

import sqlite3
import json
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS online_team_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                normalized_name TEXT NOT NULL UNIQUE,
                team_name TEXT NOT NULL,
                country TEXT NOT NULL,
                league TEXT NOT NULL,
                coach TEXT NOT NULL,
                base_formation TEXT NOT NULL,
                style TEXT NOT NULL,
                confidence TEXT NOT NULL,
                status TEXT NOT NULL,
                search_status TEXT NOT NULL,
                source_count INTEGER NOT NULL,
                online_payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS own_team_setting (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                ref TEXT NOT NULL,
                updated_at TEXT NOT NULL
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
    online_profile = None
    if payload.get("team_id") is not None:
        selected_team = get_team(int(payload["team_id"]))
    if selected_team is None:
        selected_team = find_team_by_name(payload["team_name"])
    if selected_team is None:
        online_profile = get_online_profile_by_name(payload["team_name"])
    if selected_team is None:
        if online_profile is None:
            raise HTTPException(
                status_code=422,
                detail="Time nao encontrado na base local. Salve o perfil online antes de registrar a analise.",
            )
        selected_team = {
            "id": 0,
            "name": online_profile["name"],
            "league": online_profile["league"],
            "base_formation": online_profile["base_formation"],
            "confidence": online_profile["confidence"],
        }

    created_at = datetime.now(timezone.utc).isoformat()
    status = "Concluida" if selected_team["id"] else "Concluida - perfil online"
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
                status,
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
        "status": status,
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


def normalize_team_name(name: str) -> str:
    return " ".join(name.casefold().strip().split())


def get_online_profile_by_name(team_name: str) -> dict | None:
    init_db()
    normalized = normalize_team_name(team_name)
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM online_team_profiles
            WHERE normalized_name = ?
            """,
            (normalized,),
        ).fetchone()
    return _online_profile_from_row(row) if row else None


def get_online_profile_by_id(profile_id: int) -> dict | None:
    init_db()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM online_team_profiles
            WHERE id = ?
            """,
            (profile_id,),
        ).fetchone()
    return _online_profile_from_row(row) if row else None


def list_online_profiles(query: str = "") -> list[dict]:
    init_db()
    normalized = normalize_team_name(query)
    with get_connection() as connection:
        if normalized:
            rows = connection.execute(
                """
                SELECT *
                FROM online_team_profiles
                WHERE normalized_name LIKE ?
                ORDER BY datetime(updated_at) DESC, id DESC
                """,
                (f"%{normalized}%",),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM online_team_profiles
                ORDER BY datetime(updated_at) DESC, id DESC
                """
            ).fetchall()
    return [_online_profile_from_row(row) for row in rows]


def save_online_profile(payload: dict) -> dict:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    team_name = payload["team_name"].strip()
    normalized = normalize_team_name(team_name)
    online_payload = payload.get("online_search") or {}
    sources = online_payload.get("sources") or []
    summary = payload.get("style") or online_payload.get("summary") or "Fonte tatica salva para revisao futura."

    values = {
        "normalized_name": normalized,
        "team_name": team_name,
        "country": payload.get("country") or "A confirmar",
        "league": payload.get("league") or "Fonte publica",
        "coach": payload.get("coach") or "A confirmar",
        "base_formation": payload.get("base_formation") or "A definir",
        "style": summary,
        "confidence": payload.get("confidence") or ("Medio" if online_payload.get("status") == "available" else "Baixo"),
        "status": payload.get("status") or "Perfil online salvo",
        "search_status": online_payload.get("status") or "saved",
        "source_count": len(sources),
        "online_payload": json.dumps(online_payload, ensure_ascii=False),
    }

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id, created_at FROM online_team_profiles WHERE normalized_name = ?",
            (normalized,),
        ).fetchone()
        if existing:
            connection.execute(
                """
                UPDATE online_team_profiles
                SET team_name = ?, country = ?, league = ?, coach = ?, base_formation = ?,
                    style = ?, confidence = ?, status = ?, search_status = ?, source_count = ?,
                    online_payload = ?, updated_at = ?
                WHERE normalized_name = ?
                """,
                (
                    values["team_name"],
                    values["country"],
                    values["league"],
                    values["coach"],
                    values["base_formation"],
                    values["style"],
                    values["confidence"],
                    values["status"],
                    values["search_status"],
                    values["source_count"],
                    values["online_payload"],
                    now,
                    normalized,
                ),
            )
            profile_id = existing["id"]
        else:
            cursor = connection.execute(
                """
                INSERT INTO online_team_profiles (
                    normalized_name, team_name, country, league, coach, base_formation,
                    style, confidence, status, search_status, source_count, online_payload,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["normalized_name"],
                    values["team_name"],
                    values["country"],
                    values["league"],
                    values["coach"],
                    values["base_formation"],
                    values["style"],
                    values["confidence"],
                    values["status"],
                    values["search_status"],
                    values["source_count"],
                    values["online_payload"],
                    now,
                    now,
                ),
            )
            profile_id = cursor.lastrowid

    saved = get_online_profile_by_name(team_name)
    if saved:
        return saved
    return {"id": profile_id, **values, "created_at": now, "updated_at": now}


def _online_profile_from_row(row: sqlite3.Row) -> dict:
    payload = json.loads(row["online_payload"] or "{}")
    return {
        "id": f"online-{row['id']}",
        "online_profile_id": row["id"],
        "profile_type": "online",
        "name": row["team_name"],
        "country": row["country"],
        "league": row["league"],
        "coach": row["coach"],
        "base_formation": row["base_formation"],
        "style": row["style"],
        "confidence": row["confidence"],
        "status": row["status"],
        "search_status": row["search_status"],
        "source_count": row["source_count"],
        "crest_url": payload.get("crest_url"),
        "online_search": payload,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_own_team_ref() -> str | None:
    init_db()
    with get_connection() as connection:
        row = connection.execute("SELECT ref FROM own_team_setting WHERE id = 1").fetchone()
    return row["ref"] if row else None


def set_own_team_ref(ref: str) -> str:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO own_team_setting (id, ref, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET ref = excluded.ref, updated_at = excluded.updated_at
            """,
            (ref, now),
        )
    return ref
