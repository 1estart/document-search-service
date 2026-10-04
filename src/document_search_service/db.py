import asyncio
import threading
import asyncpg
import json
from collections.abc import Iterable
from datetime import datetime

from .config import settings
from .models import Document


class _AsyncRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

runner = _AsyncRunner()

pool: asyncpg.Pool | None = None

async def _get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(settings.database_url)
    return pool


def init_db() -> None:
    async def _init():
        p = await _get_pool()
        async with p.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    rubrics TEXT NOT NULL DEFAULT '[]',
                    text TEXT NOT NULL,
                    created_date TIMESTAMPTZ NOT NULL
                )
            """)
    runner.run(_init())


def upsert_document(document: Document) -> None:
    async def _upsert():
        p = await _get_pool()
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
    runner.run(_upsert())


def get_documents_by_ids(ids: Iterable[str]) -> list[Document]:
    id_list = list(ids)
    if not id_list:
        return []
    
    async def _get():
        p = await _get_pool()
        async with p.acquire() as conn:
            # ANY($1) - эффективный поиск по массиву ID в Postgres
            rows = await conn.fetch(
                "SELECT id, rubrics, text, created_date FROM documents WHERE id = ANY($1)",
                id_list
            )
            rows_by_id = {row["id"]: row for row in rows}
            result = []
            for doc_id in id_list:
                if doc_id in rows_by_id:
                    row = rows_by_id[doc_id]
                    result.append(Document(
                        id=row["id"],
                        rubrics=json.loads(row["rubrics"]),
                        text=row["text"],
                        created_date=row["created_date"],
                    ))
            return result
            
    return runner.run(_get())


def delete_document(document_id: str) -> None:
    async def _delete():
        p = await _get_pool()
        async with p.acquire() as conn:
            await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
    runner.run(_delete())