"""Focused tests: replay envelope + shadow telemetry for C5 Retrieval Coverage MVP.

Covers:
  - EnvelopeBuilder.with_coverage_scorer() binds 'coverage_scorer' role
  - Two distinct versions produce distinct hashes
  - Envelope hash changes when scorer version changes (C1 determinism invariant)
  - Same version is idempotent
  - mode=off produces zero coverage captures in ShadowEvaluationResult
  - shadow snapshot coverage_captures field populated from scorer buffer
  - ShadowEvaluationResult.to_dict() exposes coverage_summary when captures present
  - ShadowEvaluationResult.to_dict() omits coverage_summary when no captures
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Replay envelope tests
# ---------------------------------------------------------------------------

from agentic_core.L2_execution.determinism.replay_envelope import EnvelopeBuilder


def _valid_builder() -> EnvelopeBuilder:
    return EnvelopeBuilder().with_replay_key("rk-test").with_policy_hash("ph-test").with_run_id("run-test")


def test_with_coverage_scorer_binds_role() -> None:
    envelope = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    assert "coverage_scorer" in envelope.ml_model_hashes


def test_with_coverage_scorer_hash_is_hex16() -> None:
    envelope = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    h = envelope.ml_model_hashes["coverage_scorer"]
    assert len(h) == 16
    assert all(c in "0123456789abcdef" for c in h)


def test_with_coverage_scorer_matches_expected_digest() -> None:
    version = "heuristic-v0.1.0"
    expected = hashlib.sha256(version.encode()).hexdigest()[:16]
    envelope = _valid_builder().with_coverage_scorer(version).build()
    assert envelope.ml_model_hashes["coverage_scorer"] == expected


def test_different_versions_produce_different_hashes() -> None:
    env_a = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    env_b = _valid_builder().with_coverage_scorer("heuristic-v0.2.0").build()
    assert env_a.ml_model_hashes["coverage_scorer"] != env_b.ml_model_hashes["coverage_scorer"]


def test_envelope_digest_changes_with_scorer_version() -> None:
    env_a = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    env_b = _valid_builder().with_coverage_scorer("heuristic-v0.2.0").build()
    assert env_a.envelope_hash() != env_b.envelope_hash()


def test_same_version_is_idempotent() -> None:
    env_a = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    env_b = _valid_builder().with_coverage_scorer("heuristic-v0.1.0").build()
    assert env_a.ml_model_hashes["coverage_scorer"] == env_b.ml_model_hashes["coverage_scorer"]


def test_no_scorer_version_has_no_coverage_key() -> None:
    envelope = _valid_builder().build()
    assert "coverage_scorer" not in envelope.ml_model_hashes


# ---------------------------------------------------------------------------
# ShadowEvaluationResult coverage_captures field tests
# (unit-level — built with mock objects; no full evaluation run needed)
# ---------------------------------------------------------------------------

try:
    from agentic_core.utils.workflow_engines.shadow_eval_runner import ShadowEvaluationResult
    from agentic_core.utils.workflow_engines.snapshots import RetrievalDriftSnapshot

    _SHADOW_AVAILABLE = True
except ImportError:
    _SHADOW_AVAILABLE = False
    ShadowEvaluationResult = None  # type: ignore[assignment,misc]
    RetrievalDriftSnapshot = None  # type: ignore[assignment,misc]

_skip_shadow = pytest.mark.skipif(
    not _SHADOW_AVAILABLE,
    reason="shadow_eval_runner transitive deps not available in this env",
)


def _mock_delta_report() -> MagicMock:
    dr = MagicMock()
    dr.metric_deltas = {}
    dr.to_dict.return_value = {"metric_deltas": {}}
    return dr


def _mock_eval_report() -> MagicMock:
    er = MagicMock()
    er.aggregate_scores = {}
    er.per_example_results = []
    return er


def _minimal_snapshot() -> RetrievalDriftSnapshot:
    return RetrievalDriftSnapshot(
        timestamp="2026-01-01T00:00:00Z",
        system_version="v1",
        retrieval_hit_rate=0.0,
        score_distribution_mean=0.0,
        score_distribution_std=0.0,
        top_k_stability=0.0,
        sample_size=0,
    )


def _build_result(coverage_captures: list | None = None) -> ShadowEvaluationResult:
    snap = _minimal_snapshot()
    return ShadowEvaluationResult(
        delta_report=_mock_delta_report(),
        baseline_report=_mock_eval_report(),
        candidate_report=_mock_eval_report(),
        baseline_retrieval_snapshot=snap,
        candidate_retrieval_snapshot=snap,
        candidate_alerts=[],
        coverage_captures=coverage_captures,
    )


@_skip_shadow
def test_coverage_captures_defaults_to_empty_list() -> None:
    result = _build_result()
    assert result.coverage_captures == []


@_skip_shadow
def test_coverage_captures_none_normalised_to_empty_list() -> None:
    result = _build_result(coverage_captures=None)
    assert result.coverage_captures == []


@_skip_shadow
def test_to_dict_has_coverage_capture_count_zero() -> None:
    result = _build_result()
    d = result.to_dict()
    assert d["coverage_capture_count"] == 0
    assert d["coverage_summary"] == {}


@_skip_shadow
def test_to_dict_coverage_summary_populated_when_captures_present() -> None:
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        ShadowTrainingCapture,
    )

    cap = ShadowTrainingCapture(
        run_id="test-run",
        query_id="q0",
        chunk_ids=("c0", "c1", "c2", "c3", "c4"),
        sim_mean=0.75,
        sim_std=0.05,
        sim_min=0.65,
        sim_max=0.85,
        coverage_score=0.78,
        should_rerank=False,
        rerank_triggered=False,
        gap_signal="ok",
        evaluator_version="heuristic-v0.1.0",
        latency_ms=4.2,
        budget_status="ok",
        fallback_reason="",
        x1d_groundedness_hook=-1.0,
        captured_at_utc=time.time(),
    )
    result = _build_result(coverage_captures=[cap])
    d = result.to_dict()
    assert d["coverage_capture_count"] == 1
    s = d["coverage_summary"]
    assert s["capture_count"] == 1
    assert s["score_mean"] == pytest.approx(0.78, abs=1e-4)
    assert s["rerank_triggered_count"] == 0
    assert s["budget_exceeded_count"] == 0
    assert "heuristic-v0.1.0" in s["evaluator_versions"]


@_skip_shadow
def test_to_dict_coverage_summary_aggregates_multiple_captures() -> None:
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        ShadowTrainingCapture,
    )

    def _cap(score: float, rerank: bool, budget: str) -> ShadowTrainingCapture:
        return ShadowTrainingCapture(
            run_id="test-run",
            query_id="q0",
            chunk_ids=("c0", "c1", "c2"),
            sim_mean=score,
            sim_std=0.0,
            sim_min=score,
            sim_max=score,
            coverage_score=score,
            should_rerank=rerank,
            rerank_triggered=rerank,
            gap_signal="",
            evaluator_version="heuristic-v0.1.0",
            latency_ms=1.0,
            budget_status=budget,
            fallback_reason="",
            x1d_groundedness_hook=-1.0,
            captured_at_utc=time.time(),
        )

    caps = [_cap(0.6, False, "ok"), _cap(0.4, True, "ok"), _cap(0.5, False, "budget_exceeded")]
    result = _build_result(coverage_captures=caps)
    d = result.to_dict()
    s = d["coverage_summary"]
    assert s["capture_count"] == 3
    assert s["score_mean"] == pytest.approx(0.5, abs=1e-4)
    assert s["rerank_triggered_count"] == 1
    assert s["budget_exceeded_count"] == 1


# ---------------------------------------------------------------------------
# off mode emits no scorer metadata; shadow mode drains into result
# ---------------------------------------------------------------------------

from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
    drain_shadow_buffer,
    score_coverage,
)


@dataclass
class _FakeChunk:
    chunk_id: str
    combined_score: float


def _chunks(scores: list[float]) -> list[_FakeChunk]:
    return [_FakeChunk(chunk_id=f"c{i}", combined_score=s) for i, s in enumerate(scores)]


@_skip_shadow
def test_mode_off_leaves_buffer_empty_so_result_has_zero_captures() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "off"}):
        score_coverage(_chunks([0.2, 0.3, 0.1]))
    result = _build_result(coverage_captures=drain_shadow_buffer())
    assert result.coverage_captures == []
    assert result.to_dict()["coverage_capture_count"] == 0


@_skip_shadow
def test_shadow_mode_buffer_drains_into_result() -> None:
    drain_shadow_buffer()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        score_coverage(_chunks([0.7, 0.8, 0.75]))
    caps = drain_shadow_buffer()
    result = _build_result(coverage_captures=caps)
    assert result.coverage_captures
    d = result.to_dict()
    assert d["coverage_capture_count"] == len(caps)
    assert "score_mean" in d["coverage_summary"]
    assert "evaluator_versions" in d["coverage_summary"]


# ---------------------------------------------------------------------------
# E1 bind: wire_coverage_scorer_to_envelope()
# ---------------------------------------------------------------------------


def test_wire_coverage_scorer_to_envelope_shadow_mode_binds_hash() -> None:
    """Shadow mode: wire_coverage_scorer_to_envelope() calls with_coverage_scorer()."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        wire_coverage_scorer_to_envelope,
    )
    from unittest.mock import MagicMock

    builder = MagicMock()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        wire_coverage_scorer_to_envelope(builder)
    builder.with_coverage_scorer.assert_called_once()


def test_wire_coverage_scorer_to_envelope_advisory_active_mode_binds_hash() -> None:
    """Advisory active mode: version hash is bound."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        wire_coverage_scorer_to_envelope,
    )
    from unittest.mock import MagicMock

    builder = MagicMock()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "advisory_active"}):
        wire_coverage_scorer_to_envelope(builder)
    builder.with_coverage_scorer.assert_called_once()


def test_wire_coverage_scorer_to_envelope_off_mode_is_noop() -> None:
    """Off mode: with_coverage_scorer() must NOT be called."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        wire_coverage_scorer_to_envelope,
    )
    from unittest.mock import MagicMock

    builder = MagicMock()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "off"}):
        wire_coverage_scorer_to_envelope(builder)
    builder.with_coverage_scorer.assert_not_called()


def test_wire_coverage_scorer_to_envelope_none_builder_is_noop() -> None:
    """None builder: must not raise."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        wire_coverage_scorer_to_envelope,
    )

    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        wire_coverage_scorer_to_envelope(None)  # must not raise


def test_wire_coverage_scorer_to_envelope_passes_correct_version() -> None:
    """Version string passed to with_coverage_scorer matches _EVALUATOR_VERSION."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        _EVALUATOR_VERSION,
        wire_coverage_scorer_to_envelope,
    )
    from unittest.mock import MagicMock

    builder = MagicMock()
    with patch.dict("os.environ", {"COVERAGE_SCORER_MODE": "shadow"}):
        wire_coverage_scorer_to_envelope(builder)
    builder.with_coverage_scorer.assert_called_once_with(_EVALUATOR_VERSION)
