"""apps-test-model: APP CONTRACT.

Deprecated Tavily shim tests for apps_research.
"""

from __future__ import annotations

import pytest

from apps_research.integrations.tavily_retrieval import RetrievedDoc, retrieve


def test_tavily_retrieve_is_disabled_even_when_called_directly(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "unused")

    with pytest.raises(RuntimeError, match="Tavily retrieval is deprecated and disabled"):
        retrieve("Anthropic partnerships", top_k=5)


def test_legacy_retrieved_doc_shape_remains_importable():
    doc = RetrievedDoc(
        url="https://example.com",
        title="Example",
        snippet="legacy shape only",
        score=0.1,
    )

    assert doc.url == "https://example.com"
    assert doc.title == "Example"
