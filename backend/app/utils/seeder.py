from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from elasticsearch import Elasticsearch


def seed_elasticsearch(es: Elasticsearch, seed_file: Path) -> None:
    if not seed_file.exists():
        return
    data: Dict[str, Any] = json.loads(seed_file.read_text())
    for index_name, documents in data.items():
        es.indices.create(index=index_name, ignore=400)
        for doc in documents:
            doc_id = doc.get("id")
            es.index(index=index_name, id=doc_id, document=doc)
