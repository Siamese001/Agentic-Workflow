"""Legacy tests for dormant apps_research.integrations.tavily_retrieval (plan P1.2).

The live Tavily call is opt-in via ``APPS_RESEARCH_LEGACY_TAVILY_TEST=1`` so
normal test runs do not exercise the deprecated provider.
"""

from __future__ import annotations

import os

import pytest

from apps_research.integrations.tavily_retrieval import RetrievedDoc, retrieve


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
        retrieve("Blend360 agentic AI")


def test_empty_subquery_raises(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    with pytest.raises(ValueError):
        retrieve("", top_k=5)


def _tavily_sdk_available() -> bool:
    try:
        import tavily  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.mark.skipif(
    os.environ.get("APPS_RESEARCH_LEGACY_TAVILY_TEST", "").strip() not in {"1", "true", "yes", "on"}
    or not os.environ.get("TAVILY_API_KEY", "").strip()
    or not _tavily_sdk_available(),
    reason="legacy Tavily live test is opt-in and needs TAVILY_API_KEY + tavily-python",
)
def test_live_retrieval_returns_docs():
    docs = retrieve("Blend360 agentic AI transformation services", top_k=10)
    assert isinstance(docs, list)
    assert len(docs) >= 5
    for d in docs:
        assert isinstance(d, RetrievedDoc)
        assert d.url.startswith("http")
