import os

import hashlib
import json
import sqlite3

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
# DATABASE_PATH = BACKEND_DIR / "resume_metadata.db" Original

# Testing DB
DATABASE_PATH = Path(
    os.getenv(
        "RESUME_DATABASE_PATH",
        str(BACKEND_DIR / "resume_metadata.db"),
    )
)

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                resume_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL UNIQUE,
                parsed_resume TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def calculate_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def create_resume(
    resume_id: str,
    filename: str,
    file_hash: str,
    parsed_resume: dict[str, Any],
) -> dict:
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO resumes (
                resume_id, filename, file_hash,
                parsed_resume, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resume_id,
                filename,
                file_hash,
                json.dumps(parsed_resume),
                now,
                now,
            ),
        )

    return get_resume(resume_id)


def get_resume(resume_id: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM resumes WHERE resume_id = ?",
            (resume_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def get_resume_by_hash(file_hash: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM resumes WHERE file_hash = ?",
            (file_hash,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def list_resumes() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT resume_id, filename, parsed_resume,
                   created_at, updated_at
            FROM resumes
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def delete_resume(resume_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM resumes WHERE resume_id = ?",
            (resume_id,),
        )

    return cursor.rowcount > 0


def _row_to_dict(row) -> dict:
    result = dict(row)
    result["parsed_resume"] = json.loads(result["parsed_resume"])
    return result
