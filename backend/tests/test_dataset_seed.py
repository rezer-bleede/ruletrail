import json
from pathlib import Path

from app.core import config as config_module
from backend.tests.conftest import FakeElasticsearch


def test_seed_demo_endpoint(client, monkeypatch, tmp_path):
    seed_payload = {"demo-index": [{"id": "1", "field": "value"}]}
    seed_file = tmp_path / "seed.json"
    seed_file.write_text(json.dumps(seed_payload))

    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()
    settings = config_module.get_settings()
    settings.seed_es_path = str(seed_file)
    settings.elasticsearch_hosts = ["http://mock-es"]

    fake_es = FakeElasticsearch([])

    def _fake_es_client(hosts):  # noqa: ANN001 - signature dictated by Elasticsearch
        assert hosts == settings.elasticsearch_hosts
        return fake_es

    import app.api.v1.datasets as datasets_module

    monkeypatch.setattr(datasets_module, "Elasticsearch", _fake_es_client)
    monkeypatch.setattr(datasets_module, "get_settings", lambda: settings)

    response = client.post("/api/datasets/seed-demo")
    assert response.status_code == 200
    payload = response.json()
    assert payload["indexed"] == 1
    assert Path(payload["source"]) == seed_file
    assert fake_es.indices.created == ["demo-index"]
    assert fake_es.indexed[0]["document"]["field"] == "value"


def test_seed_demo_missing_file(client, monkeypatch, tmp_path):
    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()
    settings = config_module.get_settings()
    settings.seed_es_path = str(tmp_path / "missing.json")

    import app.api.v1.datasets as datasets_module

    monkeypatch.setattr(datasets_module, "Elasticsearch", lambda hosts: FakeElasticsearch([]))
    monkeypatch.setattr(datasets_module, "get_settings", lambda: settings)

    response = client.post("/api/datasets/seed-demo")
    assert response.status_code == 404


def test_seed_demo_uses_default_path_from_backend(monkeypatch, client):
    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()

    settings = config_module.Settings()
    settings.elasticsearch_hosts = ["http://mock-es"]

    import app.api.v1.datasets as datasets_module

    fake_es = FakeElasticsearch([])

    monkeypatch.setattr(datasets_module, "Elasticsearch", lambda hosts: fake_es)
    monkeypatch.setattr(datasets_module, "get_settings", lambda: settings)

    backend_dir = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(backend_dir)

    response = client.post("/api/datasets/seed-demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["indexed"] == 4
