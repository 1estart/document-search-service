import json
from collections.abc import Iterable
from datetime import datetime

import asyncpg

from .config import settings
from .models import Document


pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(settings.database_url)
    return pool


async def close_pool() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


async def init_db() -> None:
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                rubrics TEXT NOT NULL DEFAULT '[]',
                text TEXT NOT NULL,
                created_date TIMESTAMPTZ NOT NULL
            )
        """)


async def upsert_document(document: Document) -> None:
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO documents (id, rubrics, text, created_date)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE SET
                rubrics = EXCLUDED.rubrics,
                text = EXCLUDED.text,
                created_date = EXCLUDED.created_date
            """,
            document.id,
            json.dumps(document.rubrics, ensure_ascii=False),
            document.text,
            document.created_date,
        )


async def get_documents_by_ids(ids: Iterable[str]) -> list[Document]:
    id_list = list(ids)

    if not id_list:
        return []

    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, rubrics, text, created_date
            FROM documents
            WHERE id = ANY($1)
            ORDER BY created_date DESC
            """,
            id_list,
        )

    return [
        Document(
            id=row["id"],
            rubrics=json.loads(row["rubrics"]),
            text=row["text"],
            created_date=row["created_date"],
        )
        for row in rows
        ]


async def delete_document(document_id: str) -> None:
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute("DELETE FROM documents WHERE id = $1", document_id)