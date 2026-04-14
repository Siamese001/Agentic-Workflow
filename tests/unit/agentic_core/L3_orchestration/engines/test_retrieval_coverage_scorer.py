"""Tests for the advisory retrieval coverage scorer (C5 MVP).

Covers:
  - Invariant: advisory=True always
  - Score distribution for high / low similarity inputs
  - Empty-input boundary
  - Budget-exceeded fallback
  - Exception isolation (fail-closed)
  - Mode=off, mode=shadow, mode=advisory_active gating
  - EvidenceBundle field presence
  - Advisory-only boundary: no reference to retrieval_coverage in prompt_assembler.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Minimal stub for HybridSearchResult duck-typing
# ---------------------------------------------------------------------------


@dataclass
class _FakeChunk:
    chunk_id: str
    combined_score: float
    metadata: dict[str, Any] = None  # type: ignore[assignment]
    source: str = "vector"
    vector_score: float = 0.0
    lexical_score: float = 0.0

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


def _chunks(scores: list[float]) -> list[_FakeChunk]:
    return [_FakeChunk(chunk_id=f"c{i}", combined_score=s) for i, s in enumerate(scores)]


# ---------------------------------------------------------------------------
# Import under test
# ---------------------------------------------------------------------------

from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
    HeuristicCoverageScorer,
    RetrievalCoverageResult,
    _SHADOW_BUFFER,
    drain_shadow_buffer,
    get_coverage_scorer_mode,
    score_coverage,
)


# ---------------------------------------------------------------------------
# Advisory invariant
# ---------------------------------------------------------------------------


def test_result_advisory_is_always_true() -> None:
    scorer = HeuristicCoverageScorer()
    result = scorer.score(_chunks([0.9, 0.8, 0.7, 0.85, 0.75]))
    assert result.advisory is True


def test_advisory_field_raises_on_false() -> None:
    with pytest.raises(ValueError, match="advisory must always be True"):
        RetrievalCoverageResult(
            advisory=False,
            evaluator_name="x",
            evaluator_version="0.0",
            coverage_score=0.5,
            should_rerank=False,
            gap_signal="",
            latency_ms=1.0,
            budget_status="ok",
            fallback_reason="",
        )


# ---------------------------------------------------------------------------
# Score distribution
# ---------------------------------------------------------------------------


def test_high_sim_no_rerank() -> None:
    scorer = HeuristicCoverageScorer()
    result = scorer.score(_chunks([0.9, 0.85, 0.88, 0.82, 0.91]))
    assert result.coverage_score > 0.7
    assert result.should_rerank is False
    assert result.budget_status == "ok"
    assert result.fallback_reason == ""


def test_low_sim_triggers_should_rerank() -> None:
    scorer = HeuristicCoverageScorer()
    result = scorer.score(_chunks([0.2, 0.15, 0.18, 0.1, 0.22]))
    assert result.coverage_score < 0.45
    assert result.should_rerank is True


def test_mixed_sim_gap_signal_top_heavy() -> None:
    scorer = HeuristicCoverageScorer()
    result = scorer.score(_chunks([0.9, 0.1, 0.1, 0.1, 0.1]))
    assert result.gap_signal in ("top_heavy", "low_relevance", "low_sim_spread")


# ---------------------------------------------------------------------------
# Empty-input boundary
# ---------------------------------------------------------------------------


def test_empty_chunks_zero_score() -> None:
    scorer = HeuristicCoverageScorer()
    result = scorer.score([])
    assert result.coverage_score == 0.0
    assert result.should_rerank is False
    assert result.budget_status == "ok"
    assert result.gap_signal == "empty"


# ---------------------------------------------------------------------------
# Budget-exceeded fallback
# ---------------------------------------------------------------------------


class _SlowScorer:
    evaluator_name = "slow_test_scorer"
    evaluator_version = "0.0.0-test"

    def score(self, chunks: list[Any]) -> RetrievalCoverageResult:
        time.sleep(0.3)  # 300ms — way over any budget
        return RetrievalCoverageResult(
            advisory=True,
            evaluator_name=self.evaluator_name,
            evaluator_version=self.evaluator_version,
            coverage_score=0.99,
            should_rerank=False,
            gap_signal="ok",
            latency_ms=300.0,
            budget_status="ok",
            fallback_reason="",
        )


def test_budget_exceeded_returns_none() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow", "COVERAGE_SCORER_BUDGET_MS": "50"}):
        result, triggered = score_coverage(_chunks([0.5, 0.6]), scorer=_SlowScorer())
    assert result is None
    assert triggered is False
    captures = drain_shadow_buffer()
    assert len(captures) == 1
    assert captures[0].budget_status == "budget_exceeded"
    assert captures[0].fallback_reason != ""


# ---------------------------------------------------------------------------
# Exception isolation (fail-closed)
# ---------------------------------------------------------------------------


class _BrokenScorer:
    evaluator_name = "broken_test_scorer"
    evaluator_version = "0.0.0-test"

    def score(self, chunks: list[Any]) -> RetrievalCoverageResult:
        raise RuntimeError("simulated scorer failure")


def test_exception_returns_none_no_reraise() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        result, triggered = score_coverage(_chunks([0.5, 0.6]), scorer=_BrokenScorer())
    assert result is None
    assert triggered is False
    captures = drain_shadow_buffer()
    assert len(captures) == 1
    assert captures[0].budget_status == "fallback"
    assert "simulated scorer failure" in captures[0].fallback_reason


# ---------------------------------------------------------------------------
# Mode gating
# ---------------------------------------------------------------------------


def test_mode_off_skips_scorer_entirely() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "off"}):
        result, triggered = score_coverage(_chunks([0.2, 0.1, 0.15]))
    assert result is None
    assert triggered is False
    assert len(_SHADOW_BUFFER) == 0


def test_mode_shadow_no_rerank_even_if_coverage_low() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        result, triggered = score_coverage(_chunks([0.1, 0.05, 0.08]))
    assert result is not None
    assert result.advisory is True
    assert result.should_rerank is True
    assert triggered is False  # shadow mode never triggers rerank


def test_mode_advisory_active_triggers_rerank_when_coverage_low() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "advisory_active"}):
        result, triggered = score_coverage(_chunks([0.1, 0.05, 0.08]))
    assert result is not None
    assert result.should_rerank is True
    assert triggered is True  # advisory_active + should_rerank=True → trigger


def test_mode_advisory_active_no_trigger_when_coverage_high() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "advisory_active"}):
        result, triggered = score_coverage(_chunks([0.9, 0.88, 0.91, 0.87, 0.92]))
    assert result is not None
    assert result.should_rerank is False
    assert triggered is False


def test_invalid_mode_falls_back_to_shadow() -> None:
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "INVALID_MODE"}):
        mode = get_coverage_scorer_mode()
    assert mode == "shadow"


# ---------------------------------------------------------------------------
# EvidenceBundle field presence
# ---------------------------------------------------------------------------


def test_evidence_bundle_has_retrieval_coverage_field() -> None:
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import EvidenceBundle

    bundle = EvidenceBundle(
        query="test",
        collection="code_chunks",
        ranked_chunks=[],
        citation_anchors={},
        contradiction_flags=[],
        exact_match_winners=[],
        expanded_chunk_ids=[],
    )
    assert hasattr(bundle, "retrieval_coverage")
    assert bundle.retrieval_coverage is None


# ---------------------------------------------------------------------------
# Advisory-only boundary: prompt_assembler must not read retrieval_coverage
# ---------------------------------------------------------------------------


def test_coverage_result_not_in_prompt_assembler() -> None:
    import ast
    import pathlib

    assembler_path = pathlib.Path("agentic_core/prompt_governance/core/prompt_assembler.py")
    if not assembler_path.exists():
        pytest.skip("prompt_assembler.py not found — skip boundary test")

    source = assembler_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names_used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names_used.add(node.id)
        elif isinstance(node, ast.Attribute):
            names_used.add(node.attr)

    assert "retrieval_coverage" not in names_used, (
        "prompt_assembler.py must not read retrieval_coverage — advisory-only boundary violated"
    )
    assert "coverage_score" not in names_used, (
        "prompt_assembler.py must not reference coverage_score — advisory-only boundary violated"
    )
