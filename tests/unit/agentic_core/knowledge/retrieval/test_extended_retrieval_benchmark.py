"""Unit tests for Extended Retrieval Benchmark (W6.1 — G8 eval axes)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.extended_retrieval_benchmark import (
    AbstainCorrectnessResult,
    CitationPrecisionResult,
    ExtendedRetrievalBenchmark,
)


# ---------------------------------------------------------------------------
# CitationPrecisionResult
# ---------------------------------------------------------------------------

class TestCitationPrecision:

    def setup_method(self) -> None:
        self.bench = ExtendedRetrievalBenchmark(engine=None)

    def test_perfect_precision(self) -> None:
        result = self.bench.compute_citation_precision(
            query="q1",
            cited_chunk_ids=["a", "b", "c"],
            relevant_chunk_ids={"a", "b", "c"},
        )
        assert result.precision == 1.0
        assert result.false_citations == []

    def test_partial_precision(self) -> None:
        result = self.bench.compute_citation_precision(
            query="q2",
            cited_chunk_ids=["a", "b", "d"],
            relevant_chunk_ids={"a", "b", "c"},
        )
        assert abs(result.precision - 2 / 3) < 0.01
        assert result.false_citations == ["d"]

    def test_no_citations(self) -> None:
        result = self.bench.compute_citation_precision(
            query="q3",
            cited_chunk_ids=[],
            relevant_chunk_ids={"a", "b"},
        )
        assert result.precision == 1.0  # no citations = no false claims

    def test_all_false(self) -> None:
        result = self.bench.compute_citation_precision(
            query="q4",
            cited_chunk_ids=["x", "y"],
            relevant_chunk_ids={"a", "b"},
        )
        assert result.precision == 0.0
        assert len(result.false_citations) == 2


# ---------------------------------------------------------------------------
# AbstainCorrectness
# ---------------------------------------------------------------------------

class TestAbstainCorrectness:

    def setup_method(self) -> None:
        self.bench = ExtendedRetrievalBenchmark(engine=None)

    def test_correct_abstain(self) -> None:
        result = self.bench.compute_abstain_correctness(
            query="q1", should_abstain=True, did_abstain=True,
        )
        assert result.correct

    def test_correct_answer(self) -> None:
        result = self.bench.compute_abstain_correctness(
            query="q2", should_abstain=False, did_abstain=False,
        )
        assert result.correct

    def test_false_abstain(self) -> None:
        result = self.bench.compute_abstain_correctness(
            query="q3", should_abstain=False, did_abstain=True,
        )
        assert not result.correct

    def test_false_answer(self) -> None:
        result = self.bench.compute_abstain_correctness(
            query="q4", should_abstain=True, did_abstain=False,
        )
        assert not result.correct


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

class TestReports:

    def setup_method(self) -> None:
        self.bench = ExtendedRetrievalBenchmark(engine=None)

    def test_abstain_report(self) -> None:
        results = [
            AbstainCorrectnessResult(query="q1", should_abstain=True, did_abstain=True, correct=True),
            AbstainCorrectnessResult(query="q2", should_abstain=False, did_abstain=False, correct=True),
            AbstainCorrectnessResult(query="q3", should_abstain=False, did_abstain=True, correct=False),
        ]
        report = self.bench.compute_abstain_report(results)
        assert report["total"] == 3
        assert report["correct_count"] == 2
        assert abs(report["correctness_rate"] - 2 / 3) < 0.01
        assert report["false_abstains"] == 1
        assert report["false_answers"] == 0

    def test_citation_report(self) -> None:
        results = [
            CitationPrecisionResult(query="q1", cited_chunk_ids=["a"], relevant_chunk_ids={"a"}, precision=1.0),
            CitationPrecisionResult(query="q2", cited_chunk_ids=["a", "b"], relevant_chunk_ids={"a"}, precision=0.5, false_citations=["b"]),
        ]
        report = self.bench.compute_citation_report(results)
        assert report["total"] == 2
        assert abs(report["avg_precision"] - 0.75) < 0.01
        assert report["min_precision"] == 0.5
        assert report["total_false_citations"] == 1

    def test_empty_reports(self) -> None:
        assert self.bench.compute_abstain_report([])["correctness_rate"] == 1.0
        assert self.bench.compute_citation_report([])["avg_precision"] == 1.0


# ---------------------------------------------------------------------------
# Support rate
# ---------------------------------------------------------------------------

class TestSupportRate:

    def setup_method(self) -> None:
        self.bench = ExtendedRetrievalBenchmark(engine=None)

    def test_full_support(self) -> None:
        rate = self.bench.compute_support_rate([True, True, True])
        assert rate == 1.0

    def test_partial_support(self) -> None:
        rate = self.bench.compute_support_rate([True, False, True])
        assert abs(rate - 2 / 3) < 0.01

    def test_no_support(self) -> None:
        rate = self.bench.compute_support_rate([False, False])
        assert rate == 0.0

    def test_empty(self) -> None:
        rate = self.bench.compute_support_rate([])
        assert rate == 1.0

    def test_type_error_on_non_list_citations(self) -> None:
        with pytest.raises(TypeError, match="cited_chunk_ids"):
            self.bench.compute_citation_precision("q", "not_list", {"a"})  # type: ignore[arg-type]

    def test_type_error_on_non_set_relevant(self) -> None:
        with pytest.raises(TypeError, match="relevant_chunk_ids"):
            self.bench.compute_citation_precision("q", ["a"], ["a"])  # type: ignore[arg-type]

    def test_type_error_on_non_list_support(self) -> None:
        with pytest.raises(TypeError, match="sentence_supports"):
            self.bench.compute_support_rate("not_list")  # type: ignore[arg-type]

    def test_frozenset_relevant_accepted(self) -> None:
        result = self.bench.compute_citation_precision(
            query="q", cited_chunk_ids=["a"], relevant_chunk_ids=frozenset({"a"}),
        )
        assert result.precision == 1.0
