"""Unit tests for Retrieval Drift Analyzer (W6.1 — G8 drift axis)."""

from __future__ import annotations

import pytest

from tools.eval.retrieval_drift import (
    DriftReport,
    DriftResult,
    RetrievalDriftAnalyzer,
)


class TestComputeDrift:

    def setup_method(self) -> None:
        self.analyzer = RetrievalDriftAnalyzer(jaccard_threshold=0.7)

    def test_identical_results(self) -> None:
        result = self.analyzer.compute_drift(
            query="q1",
            baseline_ids=["a", "b", "c"],
            post_ids=["a", "b", "c"],
        )
        assert result.jaccard_similarity == 1.0
        assert result.ids_lost == []
        assert result.ids_gained == []
        assert result.mean_position_shift == 0.0

    def test_completely_different(self) -> None:
        result = self.analyzer.compute_drift(
            query="q2",
            baseline_ids=["a", "b", "c"],
            post_ids=["x", "y", "z"],
        )
        assert result.jaccard_similarity == 0.0
        assert len(result.ids_lost) == 3
        assert len(result.ids_gained) == 3

    def test_partial_overlap(self) -> None:
        result = self.analyzer.compute_drift(
            query="q3",
            baseline_ids=["a", "b", "c"],
            post_ids=["b", "c", "d"],
        )
        assert abs(result.jaccard_similarity - 0.5) < 0.01  # 2/4
        assert result.ids_lost == ["a"]
        assert result.ids_gained == ["d"]

    def test_position_shift(self) -> None:
        result = self.analyzer.compute_drift(
            query="q4",
            baseline_ids=["a", "b", "c"],
            post_ids=["c", "a", "b"],
        )
        assert result.jaccard_similarity == 1.0
        assert result.mean_position_shift > 0.0

    def test_empty_results(self) -> None:
        result = self.analyzer.compute_drift(
            query="q5",
            baseline_ids=[],
            post_ids=[],
        )
        assert result.jaccard_similarity == 1.0  # empty = identical

    def test_single_item(self) -> None:
        result = self.analyzer.compute_drift(
            query="q6",
            baseline_ids=["a"],
            post_ids=["a"],
        )
        assert result.jaccard_similarity == 1.0
        assert result.kendall_tau == 1.0

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="jaccard_threshold"):
            RetrievalDriftAnalyzer(jaccard_threshold=1.5)
        with pytest.raises(ValueError, match="jaccard_threshold"):
            RetrievalDriftAnalyzer(jaccard_threshold=-0.1)

    def test_type_error_on_non_list(self) -> None:
        with pytest.raises(TypeError, match="baseline_ids"):
            self.analyzer.compute_drift("q", "not_a_list", ["a"])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="post_ids"):
            self.analyzer.compute_drift("q", ["a"], "not_a_list")  # type: ignore[arg-type]

    def test_kendall_tau_reversed_order(self) -> None:
        result = self.analyzer.compute_drift(
            query="q7",
            baseline_ids=["a", "b", "c", "d"],
            post_ids=["d", "c", "b", "a"],
        )
        assert result.jaccard_similarity == 1.0
        assert result.kendall_tau < 0.0  # reversed → negative τ

    def test_duplicate_ids_handled(self) -> None:
        result = self.analyzer.compute_drift(
            query="q8",
            baseline_ids=["a", "a", "b"],
            post_ids=["a", "b", "b"],
        )
        # Sets deduplicate, so jaccard is based on unique IDs
        assert result.jaccard_similarity == 1.0  # {a,b} vs {a,b}


class TestComputeReport:

    def setup_method(self) -> None:
        self.analyzer = RetrievalDriftAnalyzer(jaccard_threshold=0.7)

    def test_empty(self) -> None:
        report = self.analyzer.compute_report([])
        assert report.total_queries == 0

    def test_aggregate(self) -> None:
        results = [
            self.analyzer.compute_drift("q1", ["a", "b"], ["a", "b"]),
            self.analyzer.compute_drift("q2", ["x", "y"], ["z", "w"]),
        ]
        report = self.analyzer.compute_report(results)
        assert report.total_queries == 2
        assert report.avg_jaccard == 0.5
        assert len(report.queries_with_high_drift) == 1  # q2

    def test_no_high_drift(self) -> None:
        results = [
            self.analyzer.compute_drift("q1", ["a", "b"], ["a", "b"]),
            self.analyzer.compute_drift("q2", ["c", "d"], ["c", "d"]),
        ]
        report = self.analyzer.compute_report(results)
        assert report.queries_with_high_drift == []
