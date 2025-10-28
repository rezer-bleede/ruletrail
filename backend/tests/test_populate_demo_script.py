import json
from pathlib import Path

import pytest

from app.core import config as config_module
from backend.tests.conftest import FakeElasticsearch


def test_populate_demo_main(monkeypatch, tmp_path, capsys):
    seed_file = tmp_path / "seed.json"
    seed_file.write_text(json.dumps({"demo": [{"id": "1"}]}))

    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()
    settings = config_module.get_settings()
    settings.seed_es_path = str(seed_file)
    settings.elasticsearch_hosts = ["http://mock-es"]

    fake_es = FakeElasticsearch([])

    def _fake_es(hosts):
        assert hosts == settings.elasticsearch_hosts
        return fake_es

    import app.scripts.populate_demo as script

    monkeypatch.setattr(script, "Elasticsearch", _fake_es)
    monkeypatch.setattr(script, "parse_args", lambda: script.argparse.Namespace(seed_path=None))

    result = script.main()
    captured = capsys.readouterr()
    assert "Indexed 1 documents" in captured.out
    assert result == 1
    assert fake_es.indexed[0]["index"] == "demo"


def test_populate_demo_missing_seed(monkeypatch, tmp_path):
    missing = tmp_path / "missing.json"
    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()
    settings = config_module.get_settings()
    settings.seed_es_path = str(missing)

    import app.scripts.populate_demo as script

    monkeypatch.setattr(script, "Elasticsearch", lambda hosts: FakeElasticsearch([]))
    monkeypatch.setattr(script, "parse_args", lambda: script.argparse.Namespace(seed_path=None))

    with pytest.raises(SystemExit) as excinfo:
        script.main()
    assert "Seed file not found" in str(excinfo.value)
