from document_search_service.db import get_connection, init_db
from document_search_service.es import INDEX_NAME, get_es_client, init_index


def smoke_sqlite() -> None:
    init_db()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO documents (id, rubrics, text, created_date)
            VALUES (?, ?, ?, ?)
            """,
            ("1", "[]", "hello sqlite", "2026-01-01T00:00:00Z"),
        )

        row = conn.execute(
            "SELECT id, text FROM documents WHERE id = ?",
            ("1",),
        ).fetchone()

        assert row is not None
        assert row["id"] == "1"
        assert row["text"] == "hello sqlite"

    print("sqlite ok")


def smoke_elasticsearch() -> None:
    es = get_es_client()

    info = es.info()
    print(f"elasticsearch ok: {info['version']['number']}")

    init_index(es)

    es.index(
        index=INDEX_NAME,
        id="1",
        refresh=True,
        document={
            "id": "1",
            "text": "hello elasticsearch",
        },
    )

    result = es.search(
        index=INDEX_NAME,
        query={
            "match": {
                "text": "elasticsearch",
            }
        },
    )

    assert result["hits"]["total"]["value"] >= 1

    print("elasticsearch index/search ok")


def main() -> None:
    smoke_sqlite()
    smoke_elasticsearch()


if __name__ == "__main__":
    main()