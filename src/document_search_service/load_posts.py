import csv
import ast
from datetime import datetime

from document_search_service.config import settings
from document_search_service.db import init_db, upsert_document
from document_search_service.es import init_index, index_document
from document_search_service.models import Document, IndexedDocument


def load_posts(csv_path: str) -> int:
    init_db()
    es = init_index()

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

            upsert_document(document)
            index_document(
                IndexedDocument(id=document_id, text=document.text),
                es=es,
                refresh=False,
            )

            count += 1

    es.indices.refresh(index=settings.es_index)

    return count


if __name__ == "__main__":
    loaded = load_posts("posts.csv")
    print(f"Loaded {loaded} posts")