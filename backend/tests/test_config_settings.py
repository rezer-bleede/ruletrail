from __future__ import annotations

import pytest

from app.core.config import DEFAULT_ELASTICSEARCH_HOST, Settings, _safe_json_loads


@pytest.mark.parametrize(
    "env_value,expected",
    [
        (None, [DEFAULT_ELASTICSEARCH_HOST]),
        ("", [DEFAULT_ELASTICSEARCH_HOST]),
        ("   ", [DEFAULT_ELASTICSEARCH_HOST]),
        ("http://a:9200", ["http://a:9200"]),
        ("http://a:9200,http://b:9200", ["http://a:9200", "http://b:9200"]),
        ("[\"http://a:9200\", \"http://b:9200\"]", ["http://a:9200", "http://b:9200"]),
    ],
)
def test_elasticsearch_hosts_parsing(
    monkeypatch: pytest.MonkeyPatch, env_value: str | None, expected: list[str]
) -> None:
    monkeypatch.delenv("ELASTICSEARCH_HOSTS", raising=False)
    monkeypatch.delenv("ELASTICSEARCH_HOST", raising=False)
    if env_value is not None:
        monkeypatch.setenv("ELASTICSEARCH_HOSTS", env_value)

    settings = Settings()

    assert settings.elasticsearch_hosts == expected
    assert settings.elasticsearch_host == expected[0]


def test_elasticsearch_host_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ELASTICSEARCH_HOSTS", raising=False)
    monkeypatch.setenv("ELASTICSEARCH_HOST", "http://solo:9200")

    settings = Settings()

    assert settings.elasticsearch_hosts == ["http://solo:9200"]
    assert settings.elasticsearch_host == "http://solo:9200"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", ""),
        ("   ", "   "),
        ("[\"http://a:9200\"]", ["http://a:9200"]),
        ("not-json", "not-json"),
    ],
)
def test_safe_json_loads(raw: str, expected: object) -> None:
    assert _safe_json_loads(raw) == expected
