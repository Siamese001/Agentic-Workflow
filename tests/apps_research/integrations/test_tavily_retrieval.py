"""Tests for apps_research.integrations.tavily_retrieval (plan P1.2).

Integration test with real Tavily is gated on ``TAVILY_API_KEY`` env —
skipped when absent to keep the default pytest run offline-clean.
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
    not os.environ.get("TAVILY_API_KEY", "").strip()
    or not _tavily_sdk_available(),
    reason="TAVILY_API_KEY not set or tavily-python SDK not installed",
)
def test_live_retrieval_returns_docs():
    docs = retrieve("Blend360 agentic AI transformation services", top_k=10)
    assert isinstance(docs, list)
    assert len(docs) >= 5
    for d in docs:
        assert isinstance(d, RetrievedDoc)
        assert d.url.startswith("http")
