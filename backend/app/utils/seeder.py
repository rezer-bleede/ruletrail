from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from elasticsearch import Elasticsearch


def seed_elasticsearch(es: Elasticsearch, seed_file: Path) -> int:
    """Populate Elasticsearch with demo documents.

    Returns the number of documents indexed so callers can surface
    progress to the UI/tests. Missing files simply return ``0`` instead
    of raising to keep the helper idempotent in environments where demo
    data is optional.
    """

    if not seed_file.exists():
        return 0
    data: Dict[str, Any] = json.loads(seed_file.read_text())
    indexed = 0
    for index_name, documents in data.items():
        es.indices.create(index=index_name, ignore=400)
        for doc in documents:
            doc_id = doc.get("id")
            es.index(index=index_name, id=doc_id, document=doc)
            indexed += 1
    return indexed
