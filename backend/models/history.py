"""
SQLite-backed query history store.
DB file: data/query_history.db (created automatically on first use).
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings

_DB_PATH = Path(settings.repo_root) / "data" / "query_history.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS query_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT    NOT NULL,
    config          TEXT    NOT NULL,
    question        TEXT    NOT NULL,
    answer          TEXT    NOT NULL,
    citations       TEXT    NOT NULL,
    latency_ms      REAL,
    retrieved_count INTEGER,
    reranked_count  INTEGER,
    created_at      TEXT    NOT NULL
);
"""


def _conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB_PATH))
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _conn() as con:
        con.execute(_CREATE_SQL)


def save_query(
    session_id: str,
    config: str,
    question: str,
    answer: str,
    citations: list,
    latency_ms: float,
    retrieved_count: int,
    reranked_count: int,
) -> int:
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO query_history
               (session_id, config, question, answer, citations,
                latency_ms, retrieved_count, reranked_count, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                session_id,
                config,
                question,
                answer,
                json.dumps(citations),
                latency_ms,
                retrieved_count,
                reranked_count,
                created_at,
            ),
        )
        return cur.lastrowid


def get_history(limit: int = 200, config: str | None = None, search: str | None = None) -> list[dict]:
    clauses = []
    params: list = []

    if config:
        clauses.append("config = ?")
        params.append(config)
    if search:
        clauses.append("(question LIKE ? OR answer LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params.append(limit)

    with _conn() as con:
        rows = con.execute(
            f"SELECT * FROM query_history {where} ORDER BY id DESC LIMIT ?",
            params,
        ).fetchall()

    return [dict(r) for r in rows]
