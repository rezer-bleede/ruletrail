from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from typing import Dict, Iterable

from ..core.config import get_settings


class ElasticsearchProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = Elasticsearch(hosts=settings.elasticsearch_hosts)

    def scan(self, index: str, query: Dict) -> Iterable[Dict]:
        return scan(self.client, index=index, query=query)

    def test_connection(self, index: str) -> Dict:
        info = self.client.info()
        count = self.client.count(index=index)
        return {"info": info, "count": count}


es_provider = ElasticsearchProvider()
