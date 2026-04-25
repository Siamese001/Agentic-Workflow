"""Unit tests for Stale Hit Rate Analyzer (W6.1 — G8 stale-hit axis)."""

from __future__ import annotations

import pytest

from tools.eval.stale_hit_rate import (
    StaleHitAnalyzer,
    StaleHitReport,
    StaleHitResult,
)


class TestComputeStaleHit:

    def setup_method(self) -> None:
        self.analyzer = StaleHitAnalyzer(stale_rate_threshold=0.1)
        self.freshness_manifest = {
            "chunk_a": "hash_a1",
            "chunk_b": "hash_b1",
            "chunk_c": "hash_c1",
        }
        self.current_hashes = {
            "chunk_a": "hash_a1",  # unchanged
            "chunk_b": "hash_b2",  # changed → stale
            # chunk_c missing from current → stale
        }

    def test_all_fresh(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q1",
            retrieved_ids=["chunk_a"],
            freshness_manifest={"chunk_a": "hash_a1"},
            current_hashes={"chunk_a": "hash_a1"},
        )
        assert result.stale_rate == 0.0
        assert result.fresh_ids == ["chunk_a"]
        assert result.stale_ids == []

    def test_stale_hash_mismatch(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q2",
            retrieved_ids=["chunk_b"],
            freshness_manifest=self.freshness_manifest,
            current_hashes=self.current_hashes,
        )
        assert result.stale_rate == 1.0
        assert "chunk_b" in result.stale_ids

    def test_stale_missing_from_manifest(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q3",
            retrieved_ids=["chunk_unknown"],
            freshness_manifest=self.freshness_manifest,
            current_hashes=self.current_hashes,
        )
        assert result.stale_rate == 1.0
        assert "chunk_unknown" in result.stale_ids

    def test_mixed(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q4",
            retrieved_ids=["chunk_a", "chunk_b", "chunk_c"],
            freshness_manifest=self.freshness_manifest,
            current_hashes=self.current_hashes,
        )
        # chunk_a=fresh, chunk_b=stale(hash mismatch), chunk_c=stale(missing)
        assert abs(result.stale_rate - 2 / 3) < 0.01
        assert len(result.fresh_ids) == 1

    def test_empty_retrieved(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q5",
            retrieved_ids=[],
            freshness_manifest=self.freshness_manifest,
            current_hashes=self.current_hashes,
        )
        assert result.stale_rate == 0.0

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="stale_rate_threshold"):
            StaleHitAnalyzer(stale_rate_threshold=1.5)
        with pytest.raises(ValueError, match="stale_rate_threshold"):
            StaleHitAnalyzer(stale_rate_threshold=-0.1)

    def test_type_error_on_non_list(self) -> None:
        with pytest.raises(TypeError, match="retrieved_ids"):
            self.analyzer.compute_stale_hit("q", "not_a_list", {}, {})  # type: ignore[arg-type]

    def test_type_error_on_non_dict_manifest(self) -> None:
        with pytest.raises(TypeError, match="freshness_manifest"):
            self.analyzer.compute_stale_hit("q", ["a"], "not_dict", {})  # type: ignore[arg-type]

    def test_type_error_on_non_dict_current(self) -> None:
        with pytest.raises(TypeError, match="current_hashes"):
            self.analyzer.compute_stale_hit("q", ["a"], {}, "not_dict")  # type: ignore[arg-type]

    def test_empty_manifest_and_hashes(self) -> None:
        result = self.analyzer.compute_stale_hit(
            query="q6",
            retrieved_ids=["a", "b"],
            freshness_manifest={},
            current_hashes={},
        )
        assert result.stale_rate == 1.0  # all orphans
        assert len(result.stale_ids) == 2


class TestComputeReport:

    def setup_method(self) -> None:
        self.analyzer = StaleHitAnalyzer(stale_rate_threshold=0.1)

    def test_empty(self) -> None:
        report = self.analyzer.compute_report([])
        assert report.total_queries == 0

    def test_aggregate(self) -> None:
        results = [
            StaleHitResult(query="q1", retrieved_ids=["a"], stale_rate=0.0),
            StaleHitResult(query="q2", retrieved_ids=["b", "c"], stale_rate=0.5),
        ]
        report = self.analyzer.compute_report(results)
        assert report.total_queries == 2
        assert report.total_chunks_retrieved == 3
        assert abs(report.avg_stale_rate - 0.25) < 0.01
        assert len(report.queries_above_threshold) == 1  # q2
