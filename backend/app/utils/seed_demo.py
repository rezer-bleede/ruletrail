import json
from pathlib import Path

from elasticsearch import Elasticsearch

from ..core.config import get_settings


def seed_elasticsearch(data_path: Path | None = None):
    settings = get_settings()
    if data_path is None:
        data_path = Path('/data/es_sample_data.json')
        if not data_path.exists():
            data_path = Path(__file__).resolve().parents[2] / 'seed' / 'es_sample_data.json'
    if not data_path.exists():
        return
    payload = json.loads(data_path.read_text())
    client = Elasticsearch(hosts=settings.elasticsearch_hosts)
    index = payload['index']
    if not client.indices.exists(index=index):
        client.indices.create(index=index)
    for document in payload['documents']:
        client.index(index=index, id=document['id'], document=document)


if __name__ == '__main__':
    seed_elasticsearch()
