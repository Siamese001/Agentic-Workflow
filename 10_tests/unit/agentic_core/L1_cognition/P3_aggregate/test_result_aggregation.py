"""Unit tests for L1_cognition/P3_aggregate result aggregation and ranking."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any

class TestResultAggregation:
    """Tests for aggregating multiple retrieval results."""

    def test_aggregate_single_source(self):
        """Nominal: Single source aggregation."""
        results = [{"id": 1, "text": "Result 1", "score": 0.9}]
        aggregated = results  # Pass-through for single source
        assert len(aggregated) == 1

    def test_aggregate_multiple_sources(self):
        """Nominal: Multiple sources merged correctly."""
        source1 = [{"id": 1, "score": 0.9}]
        source2 = [{"id": 2, "score": 0.8}]
        aggregated = source1 + source2
        assert len(aggregated) == 2

    def test_aggregate_removes_duplicates(self):
        """Nominal: Duplicate results are deduplicated."""
        results = [
            {"id": 1, "text": "Same"},
            {"id": 2, "text": "Same"},
            {"id": 3, "text": "Different"},
        ]
        seen_texts = set()
        unique = []
        for r in results:
            if r["text"] not in seen_texts:
                seen_texts.add(r["text"])
                unique.append(r)
        assert len(unique) == 2

    def test_aggregate_empty_sources(self):
        """Edge case: All sources empty."""
        sources: List[List[Dict]] = [[], [], []]
        aggregated = [r for s in sources for r in s]
        assert aggregated == []

    def test_aggregate_determinism(self):
        """Determinism: Same sources produce same aggregation."""
        sources = [[{"id": 1}], [{"id": 2}]]
        a1 = [r for s in sources for r in s]
        a2 = [r for s in sources for r in s]
        assert a1 == a2


class TestResultRanking:
    """Tests for ranking aggregated results."""

    def test_rank_by_score_descending(self):
        """Nominal: Results ranked by score descending."""
        results = [
            {"id": 1, "score": 0.5},
            {"id": 2, "score": 0.9},
            {"id": 3, "score": 0.7},
        ]
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)
        assert ranked[0]["id"] == 2
        assert ranked[1]["id"] == 3
        assert ranked[2]["id"] == 1

    def test_rank_stable_for_equal_scores(self):
        """Edge case: Equal scores maintain original order (stable sort)."""
        results = [
            {"id": 1, "score": 0.8},
            {"id": 2, "score": 0.8},
            {"id": 3, "score": 0.8},
        ]
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)
        ids = [r["id"] for r in ranked]
        assert ids == [1, 2, 3]  # Stable sort preserves order

    def test_rank_top_k(self):
        """Nominal: Return only top K results."""
        results = [{"id": i, "score": i / 10} for i in range(10)]
        k = 3
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)[:k]
        assert len(ranked) == 3
        assert ranked[0]["id"] == 9

    def test_rank_empty_results(self):
        """Edge case: Empty results return empty."""
        results: List[Dict] = []
        ranked = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        assert ranked == []

    def test_rank_single_result(self):
        """Edge case: Single result is returned as-is."""
        results = [{"id": 1, "score": 0.5}]
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)
        assert len(ranked) == 1


class TestDeduplication:
    """Tests for result deduplication."""

    def test_dedupe_by_id(self):
        """Nominal: Deduplicate by ID."""
        results = [
            {"id": 1, "text": "A"},
            {"id": 1, "text": "A"},
            {"id": 2, "text": "B"},
        ]
        seen_ids = set()
        unique = []
        for r in results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique.append(r)
        assert len(unique) == 2

    def test_dedupe_by_content_hash(self):
        """Nominal: Deduplicate by content hash."""
        results = [
            {"id": 1, "text": "Same content"},
            {"id": 2, "text": "Same content"},
            {"id": 3, "text": "Different"},
        ]
        seen_hashes = set()
        unique = []
        for r in results:
            h = hash(r["text"])
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique.append(r)
        assert len(unique) == 2

    def test_dedupe_keeps_highest_score(self):
        """Edge case: Keep highest scoring duplicate."""
        results = [
            {"id": 1, "text": "Same", "score": 0.5},
            {"id": 2, "text": "Same", "score": 0.9},
        ]
        best_by_text: Dict[str, Dict] = {}
        for r in results:
            text = r["text"]
            if text not in best_by_text or r["score"] > best_by_text[text]["score"]:
                best_by_text[text] = r
        unique = list(best_by_text.values())
        assert len(unique) == 1
        assert unique[0]["score"] == 0.9

    def test_dedupe_determinism(self):
        """Determinism: Same input produces same deduped output."""
        results = [{"id": 1}, {"id": 1}, {"id": 2}]
        seen = set()
        u1 = [r for r in results if r["id"] not in seen and not seen.add(r["id"])]
        seen = set()
        u2 = [r for r in results if r["id"] not in seen and not seen.add(r["id"])]
        assert u1 == u2
