import json
import sqlite3
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .config import settings
from .models import Document


@contextmanager
def connection() -> Generator[sqlite3.Connection, None, None]:
    db_path = Path(settings.database_path)

    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
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


def _document_to_params(document: Document) -> tuple[str, str, str, str]:
    return (
        document.id,
        json.dumps(document.rubrics, ensure_ascii=False),
        document.text,
        document.created_date.isoformat(),
    )


def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        rubrics=json.loads(row["rubrics"]),
        text=row["text"],
        created_date=datetime.fromisoformat(row["created_date"]),
    )


def upsert_document(document: Document) -> None:
    with connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO documents (id, rubrics, text, created_date)
            VALUES (?, ?, ?, ?)
            """,
            _document_to_params(document),
        )


def get_documents_by_ids(ids: Iterable[str]) -> list[Document]:
    id_list = list(ids)
    if not id_list:
        return []

    placeholders = ",".join("?" * len(id_list))

    with connection() as conn:
        rows = conn.execute(
            f"""
            SELECT id, rubrics, text, created_date
            FROM documents
            WHERE id IN ({placeholders})
            """,
            id_list,
        ).fetchall()

    rows_by_id = {row["id"]: _row_to_document(row) for row in rows}
    
    return [rows_by_id[doc_id] for doc_id in id_list if doc_id in rows_by_id]


def delete_document(document_id: str) -> None:
    with connection() as conn:
        conn.execute(
            "DELETE FROM documents WHERE id = ?",
            (document_id,),
        )