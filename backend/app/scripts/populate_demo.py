"""CLI helper to push the bundled demo dataset into Elasticsearch."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import get_settings
from app.utils.seeder import seed_elasticsearch

try:  # pragma: no cover - optional import guard mirrors runtime behaviour
    from elasticsearch import Elasticsearch
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Elasticsearch client is required. Install `elasticsearch` package.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate Elasticsearch with RuleTrail demo data")
    parser.add_argument(
        "--seed", dest="seed_path", type=Path, default=None, help="Path to JSON file containing documents"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    seed_path = args.seed_path or Path(settings.seed_es_path)
    if not seed_path.exists():
        raise SystemExit(f"Seed file not found at {seed_path}")

    es = Elasticsearch(settings.elasticsearch_hosts)
    indexed = seed_elasticsearch(es, seed_path)
    print(f"Indexed {indexed} documents into Elasticsearch from {seed_path}")
    return indexed


if __name__ == "__main__":  # pragma: no cover - exercised via integration test instead
    main()
