"""apps-test-model: APP CONTRACT.

Tests for apps_research.integrations.search_retrieval.
"""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.parse

import pytest

from apps_research.integrations.search_retrieval import RetrievedDoc, retrieve


class _FakeResponse:
    def __init__(self, payload=None, *, json_error: bool = False):
        self._payload = payload if payload is not None else {}
        self._json_error = json_error

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        if self._json_error:
            return b"{"
        return json.dumps(self._payload).encode("utf-8")


def test_missing_base_url_raises(monkeypatch):
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SEARXNG_BASE_URL"):
        retrieve("Blend360 agentic AI")


def test_missing_searxng_ignores_tavily_key(monkeypatch):
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    with pytest.raises(RuntimeError) as exc_info:
        retrieve("Anthropic partnerships", top_k=3)

    message = str(exc_info.value)
    assert "SEARXNG_BASE_URL" in message
    assert "Tavily is not an apps_research fallback provider" in message


def test_empty_subquery_raises(monkeypatch):
    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    with pytest.raises(ValueError, match="sub_query"):
        retrieve("", top_k=5)


def test_invalid_top_k_raises(monkeypatch):
    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    with pytest.raises(ValueError, match="top_k"):
        retrieve("query", top_k=0)


def test_retrieve_normalizes_searxng_results(monkeypatch):
    captured = {}

    def _fake_urlopen(request, *, timeout):
        parsed = urllib.parse.urlparse(request.full_url)
        captured["url"] = urllib.parse.urlunparse(parsed._replace(query=""))
        captured["params"] = dict(urllib.parse.parse_qsl(parsed.query))
        captured["timeout"] = timeout
        return _FakeResponse(
            {
                "results": [
                    {
                        "url": "https://example.com/a",
                        "title": "A",
                        "content": "alpha",
                        "score": 0.7,
                    },
                    {
                        "url": "https://example.com/b",
                        "title": "B",
                        "content": "beta",
                    },
                    {"title": "missing url", "content": "ignored"},
                ]
            }
        )

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example/")
    monkeypatch.setenv("SEARXNG_TIMEOUT_SECONDS", "7")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.urllib.request.urlopen", _fake_urlopen)

    docs = retrieve("Blend360 agentic AI", top_k=5)

    assert captured["url"] == "https://search.example/search"
    assert captured["params"] == {"q": "Blend360 agentic AI", "format": "json"}
    assert captured["timeout"] == 7.0
    assert docs == [
        RetrievedDoc(url="https://example.com/a", title="A", snippet="alpha", score=0.7),
        RetrievedDoc(url="https://example.com/b", title="B", snippet="beta", score=0.99),
    ]


def test_retrieve_passes_optional_categories_and_engines(monkeypatch):
    captured = {}

    def _fake_urlopen(request, *, timeout):
        captured["params"] = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(request.full_url).query))
        return _FakeResponse({"results": []})

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setenv("SEARXNG_CATEGORIES", "general,news")
    monkeypatch.setenv("SEARXNG_ENGINES", "duckduckgo,brave")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.urllib.request.urlopen", _fake_urlopen)

    assert retrieve("query", top_k=1) == []
    assert captured["params"]["categories"] == "general,news"
    assert captured["params"]["engines"] == "duckduckgo,brave"


def test_forbidden_response_explains_json_format(monkeypatch):
    def _fake_urlopen(request, *, timeout):
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=io.BytesIO())

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.urllib.request.urlopen", _fake_urlopen)

    with pytest.raises(RuntimeError, match="JSON output"):
        retrieve("query")


def test_request_error_raises_runtime_error(monkeypatch):
    def _fake_urlopen(request, *, timeout):
        raise TimeoutError("slow")

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.urllib.request.urlopen", _fake_urlopen)

    with pytest.raises(RuntimeError, match="request failed"):
        retrieve("query")


def test_invalid_json_raises_runtime_error(monkeypatch):
    def _fake_urlopen(request, *, timeout):
        return _FakeResponse(json_error=True)

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.urllib.request.urlopen", _fake_urlopen)

    with pytest.raises(RuntimeError, match="not valid JSON"):
        retrieve("query")
