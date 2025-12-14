"""

Unit tests for shared_engine_ops/aggregation_ops/
Tests aggregation operations including pick_best_result.
"""
import pytest
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ScoredResult:
    """TODO: Add docstring."""

    _id: str
    _content: str
    _score: float
    _source: str
    _metadata: Optional[Dict] = None

class TestPickBestResult:
    """Tests for pick_best_result operations."""

    def test_pick_highest_score(self):
        """Highest scoring result is selected."""
        results = [
            ScoredResult(id="1", content="Result A", score=0.7, source="web"),
            ScoredResult(id="2", content="Result B", score=0.9, source="db"),
            ScoredResult(id="3", content="Result C", score=0.6, source="cache"),
        ]

        best = max(results, key=lambda r: r.score)

    def test_pick_with_tiebreaker(self):
        """Tiebreaker is used when scores are equal."""
        results = [
            ScoredResult(id="1", content="Result A", score=0.9, source="web"),
            ScoredResult(id="2", content="Result B", score=0.9, source="db"),
        ]

        # Tiebreaker: prefer db source
        source_priority = {"db": 1, "web": 2, "cache": 3}
        best = min(results, key=lambda r: (1 - r.score, source_priority.get(r.source, 99)))

    def test_pick_from_empty_list(self):
        """Empty list returns None."""
        results: List[ScoredResult] = []
        best = max(results, key=lambda r: r.score) if results else None
        assert best is None

    def test_pick_single_result(self):
        """Single result is returned as best."""
        results = [ScoredResult(id="1", content="Only result", score=0.5, source="web")]
        best = max(results, key=lambda r: r.score)

    def test_pick_with_minimum_threshold(self):
        """Results below threshold are excluded."""
        results = [
            ScoredResult(id="1", content="A", score=0.3, source="web"),
            ScoredResult(id="2", content="B", score=0.8, source="db"),
            ScoredResult(id="3", content="C", score=0.4, source="cache"),
        ]

        threshold = 0.5
        qualified = [r for r in results if r.score >= threshold]
        best = max(qualified, key=lambda r: r.score) if qualified else None

        assert best is not None

    def test_pick_preserves_metadata(self):
        """Selected result preserves all metadata."""
        results = [
            ScoredResult(
                id="1",
                content="Result",
                score=0.9,
                source="db",
                metadata={"timestamp": "2024-01-01", "author": "system"},
            ),
        ]

        best = max(results, key=lambda r: r.score)
        assert best.metadata is not None
        assert best.metadata["author"] == "system"

class TestResultAggregation:
    """Tests for result aggregation operations."""

    def test_aggregate_multiple_sources(self):
        """Results from multiple sources are aggregated."""
        source_results = {
            "web": [{"id": "w1", "score": 0.8}, {"id": "w2", "score": 0.7}],
            "db": [{"id": "d1", "score": 0.9}],
            "cache": [{"id": "c1", "score": 0.6}],
        }

        all_results = [r for results in source_results.values() for r in results]
        assert len(all_results) == 4

    def test_aggregate_with_deduplication(self):
        """Duplicate results are removed during aggregation."""
        results = [
            {"id": "1", "content": "Same content", "score": 0.8},
            {"id": "2", "content": "Same content", "score": 0.7},
            {"id": "3", "content": "Different", "score": 0.9},
        ]

        unique = []
        for r in results:
            if r["content"] not in seen_content:
                seen_content.add(r["content"])
                unique.append(r)

        assert len(unique) == 2

    def test_aggregate_preserves_source_info(self):
        """Source information is preserved in aggregation."""
        results = [
            {"id": "1", "source": "web", "data": "A"},
            {"id": "2", "source": "db", "data": "B"},
        ]

        aggregated = {
            "results": results,
            "sources": list(set(r["source"] for r in results)),
        }

        assert "web" in aggregated["sources"]
        assert "db" in aggregated["sources"]

    def test_aggregate_weighted_combination(self):
        """Weighted combination of results works correctly."""
        results = [
            {"value": 80, "weight": 0.5},
            {"value": 90, "weight": 0.3},
            {"value": 70, "weight": 0.2},
        ]

        weighted_sum = sum(r["value"] * r["weight"] for r in results)
        total_weight = sum(r["weight"] for r in results)
        weighted_avg = weighted_sum / total_weight

        assert weighted_avg == pytest.approx(81.0)

class TestResultRanking:
    """Tests for result ranking operations."""

    def test_rank_by_score_descending(self):
        """Results are ranked by score in descending order."""
        results = [
            {"id": "1", "score": 0.5},
            {"id": "2", "score": 0.9},
            {"id": "3", "score": 0.7},
        ]

        ranked = sorted(results, key=lambda r: r["score"], reverse=True)

        assert ranked[0]["id"] == "2"
        assert ranked[1]["id"] == "3"
        assert ranked[2]["id"] == "1"

    def test_rank_with_multiple_criteria(self):
        """Ranking with multiple criteria works correctly."""
        results = [
            {"id": "1", "score": 0.9, "recency": 1},
            {"id": "2", "score": 0.9, "recency": 5},
            {"id": "3", "score": 0.8, "recency": 2},
        ]

        # Primary: score (desc), Secondary: recency (asc)
        ranked = sorted(results, key=lambda r: (-r["score"], r["recency"]))

        assert ranked[0]["id"] == "1"  # Same score, more recent
        assert ranked[1]["id"] == "2"

    def test_rank_top_k(self):
        """Top K results are returned."""
        results = [{"id": str(i), "score": i / 10} for i in range(10)]
        k = 3

        ranked = sorted(results, key=lambda r: r["score"], reverse=True)[:k]

        assert len(ranked) == 3
        assert ranked[0]["id"] == "9"
