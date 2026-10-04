import ast
import asyncio
import csv
from datetime import datetime

from .config import settings
from .db import close_pool, init_db, upsert_document
from .es import close_es_client, index_document, init_index
from .models import Document, IndexedDocument


async def load_posts_async(csv_path: str) -> int:
    await init_db()
    await init_index()

    count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, start=1):
            document_id = str(idx)

            rubrics_raw = row.get("rubrics", "[]")
            try:
                rubrics = ast.literal_eval(rubrics_raw)
            except (ValueError, SyntaxError):
                rubrics = []

            document = Document(
                id=document_id,
                rubrics=rubrics,
                text=row.get("text", ""),
                created_date=datetime.strptime(
                    row["created_date"], "%Y-%m-%d %H:%M:%S"
                ),
            )

            await upsert_document(document)
            await index_document(
                IndexedDocument(id=document_id, text=document.text),
                refresh=False,
            )

            count += 1

    es = await __import__("document_search_service.es", fromlist=["get_es_client"]).get_es_client()
    await es.indices.refresh(index=settings.es_index)

    await close_pool()
    await close_es_client()

    return count


def load_posts(csv_path: str) -> int:
    return asyncio.run(load_posts_async(csv_path))


if __name__ == "__main__":
    loaded = load_posts("posts.csv")
    print(f"Loaded {loaded} posts")