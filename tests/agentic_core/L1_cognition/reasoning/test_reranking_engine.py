"""Tests for reranking_engine - search result reranking."""
import pytest
from unittest.mock import Mock
from agentic_core.L1_cognition.reasoning.reranking_engine import RerankingEngine


class TestRerankingEngine:
    def test_init(self):
        r = RerankingEngine()
        assert r is not None

    def test_rerank_results(self):
        r = RerankingEngine()
        results = [
            {"id": "1", "score": 0.5},
            {"id": "2", "score": 0.9}
        ]
        ranked = r.rerank(query="x", results=results)
        assert len(ranked) == 2

    def test_rerank_orders_by_score(self):
        r = RerankingEngine()
        results = [
            {"id": "1", "score": 0.5},
            {"id": "2", "score": 0.9}
        ]
        ranked = r.rerank(query="x", results=results)
        assert ranked[0]["score"] >= ranked[-1]["score"]

    def test_rerank_empty(self):
        r = RerankingEngine()
        assert r.rerank(query="x", results=[]) == []

    def test_top_k(self):
        r = RerankingEngine()
        results = [{"id": str(i), "score": i * 0.1} for i in range(10)]
        top = r.rerank(query="x", results=results, top_k=3)
        assert len(top) == 3

    def test_with_custom_scorer(self):
        r = RerankingEngine()
        scorer = Mock()
        scorer.score.return_value = 0.5
        r.set_scorer(scorer)
        results = [{"id": "1", "score": 0.1}]
        ranked = r.rerank(query="x", results=results)
        assert len(ranked) == 1

    def test_threshold_filter(self):
        r = RerankingEngine()
        results = [{"id": "1", "score": 0.1}, {"id": "2", "score": 0.9}]
        ranked = r.rerank(query="x", results=results, threshold=0.5)
        assert all(r_["score"] >= 0.5 for r_ in ranked)
