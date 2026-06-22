"""apps-test-model: APP CONTRACT.

Tests for apps_research.integrations.search_retrieval.
"""

from __future__ import annotations

import pytest
import requests

from apps_research.integrations.search_retrieval import RetrievedDoc, retrieve


class _FakeResponse:
    def __init__(self, payload=None, *, status_code: int = 200, json_error: bool = False):
        self._payload = payload if payload is not None else {}
        self.status_code = status_code
        self._json_error = json_error

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        if self._json_error:
            raise ValueError("not json")
        return self._payload


def test_missing_base_url_raises(monkeypatch):
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SEARXNG_BASE_URL"):
        retrieve("Blend360 agentic AI")


def test_missing_searxng_uses_tavily_when_configured(monkeypatch):
    captured = {}

    def _fake_tavily(query, *, top_k):
        from apps_research.integrations.tavily_retrieval import RetrievedDoc as TavilyDoc

        captured["query"] = query
        captured["top_k"] = top_k
        return [
            TavilyDoc(
                url="https://example.com/tavily",
                title="Tavily Result",
                snippet="grounded result",
                score=0.87,
            )
        ]

    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setattr(
        "apps_research.integrations.tavily_retrieval.retrieve",
        _fake_tavily,
    )

    docs = retrieve("Anthropic partnerships", top_k=3)

    assert captured == {"query": "Anthropic partnerships", "top_k": 3}
    assert docs == [
        RetrievedDoc(
            url="https://example.com/tavily",
            title="Tavily Result",
            snippet="grounded result",
            score=0.87,
        )
    ]


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

    def _fake_get(url, *, params, timeout):
        captured["url"] = url
        captured["params"] = params
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
    monkeypatch.setattr("apps_research.integrations.search_retrieval.requests.get", _fake_get)

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

    def _fake_get(url, *, params, timeout):
        captured["params"] = params
        return _FakeResponse({"results": []})

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setenv("SEARXNG_CATEGORIES", "general,news")
    monkeypatch.setenv("SEARXNG_ENGINES", "duckduckgo,brave")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.requests.get", _fake_get)

    assert retrieve("query", top_k=1) == []
    assert captured["params"]["categories"] == "general,news"
    assert captured["params"]["engines"] == "duckduckgo,brave"


def test_forbidden_response_explains_json_format(monkeypatch):
    def _fake_get(url, *, params, timeout):
        return _FakeResponse(status_code=403)

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.requests.get", _fake_get)

    with pytest.raises(RuntimeError, match="JSON output"):
        retrieve("query")


def test_request_error_raises_runtime_error(monkeypatch):
    def _fake_get(url, *, params, timeout):
        raise requests.Timeout("slow")

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.requests.get", _fake_get)

    with pytest.raises(RuntimeError, match="request failed"):
        retrieve("query")


def test_invalid_json_raises_runtime_error(monkeypatch):
    def _fake_get(url, *, params, timeout):
        return _FakeResponse(json_error=True)

    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    monkeypatch.setattr("apps_research.integrations.search_retrieval.requests.get", _fake_get)

    with pytest.raises(RuntimeError, match="not valid JSON"):
        retrieve("query")
