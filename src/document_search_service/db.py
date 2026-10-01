import sqlite3
from pathlib import Path

DB_PATH = Path("documents.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                rubrics TEXT NOT NULL DEFAULT '[]',
                text TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
            """
        )