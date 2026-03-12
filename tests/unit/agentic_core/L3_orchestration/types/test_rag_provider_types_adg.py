"""ADG-driven tests for L3 rag_provider_types — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.types.rag_provider_types import (
    IRagProvider,
    RagDocument,
    RagQuery,
    RagResult,
)


class TestRagQuery:
    def test_creates_with_query(self):
        q = RagQuery(query="test query")
        assert q.query == "test query"

    def test_top_k_default_10(self):
        q = RagQuery(query="test")
        assert q.top_k == 10

    def test_namespace_default(self):
        q = RagQuery(query="test")
        assert q.namespace == "sovereign-core"

    def test_enable_reranking_default_true(self):
        q = RagQuery(query="test")
        assert q.enable_reranking is True

    def test_enable_caching_default_true(self):
        q = RagQuery(query="test")
        assert q.enable_caching is True

    def test_filters_default_empty(self):
        q = RagQuery(query="test")
        assert q.filters == {}

    def test_custom_top_k(self):
        q = RagQuery(query="test", top_k=5)
        assert q.top_k == 5


class TestRagDocument:
    def test_creates(self):
        doc = RagDocument(id="doc-1", text="hello world", score=0.9)
        assert doc.id == "doc-1"
        assert doc.text == "hello world"

    def test_source_default_unknown(self):
        doc = RagDocument(id="doc-1", text="text", score=0.5)
        assert doc.source == "unknown"

    def test_metadata_default_empty(self):
        doc = RagDocument(id="doc-1", text="text", score=0.5)
        assert doc.metadata == {}


class TestRagResult:
    def test_creates(self):
        docs = [RagDocument(id="d1", text="t", score=0.9)]
        r = RagResult(query="test", documents=docs, latency_ms=12.5)
        assert r.query == "test"
        assert r.latency_ms == 12.5

    def test_cached_default_false(self):
        r = RagResult(query="q", documents=[], latency_ms=0.0)
        assert r.cached is False

    def test_faithfulness_score_default_0(self):
        r = RagResult(query="q", documents=[], latency_ms=0.0)
        assert r.faithfulness_score == 0.0


class TestIRagProvider:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(IRagProvider)

    def test_has_retrieve(self):
        assert hasattr(IRagProvider, "retrieve")
