import time
import urllib.error
import urllib.request

from .config import settings
from .db import init_db
from .es import init_index


def wait_for_elasticsearch(timeout: int = 60, interval: float = 1.0) -> None:
    url = f"{settings.elasticsearch_url.rstrip('/')}/_cluster/health"
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(interval)

    raise RuntimeError(
        f"Elasticsearch at {settings.elasticsearch_url} was not ready within {timeout}s"
    )


def bootstrap() -> None:
    wait_for_elasticsearch()
    init_db()
    init_index()


if __name__ == "__main__":
    bootstrap()