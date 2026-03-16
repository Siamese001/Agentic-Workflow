"""
Tests for ShadowReplayValidator pre-activation regression guard.

Phase 2.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_shadow_replay")
_emit_applies_guardrail("p0", "test_shadow_replay", "p0_governance")
_emit_reads_policy_state("p0", "test_shadow_replay", "policy_binding")
_emit_snapshots_state("p0", "test_shadow_replay", "state_snapshot")
emit_replay_key("p0", "test_shadow_replay")
emit_determinism_digest("p0", "test_shadow_replay")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from system_learning.enforcement.shadow_replay_validator import (
    EPSILON,
    RegressionError,
    ReplayResult,
    ShadowReplayValidator,
)

_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64


def _make_result(
    trace_id: str = "t1",
    original_digest: str = _DIGEST_A,
    replayed_digest: str = _DIGEST_A,
    original_perf: float = 0.9,
    replayed_perf: float = 0.9,
    original_safety: float = 0.95,
    replayed_safety: float = 0.95,
) -> ReplayResult:
    return ReplayResult(
        trace_id=trace_id,
        original_digest=original_digest,
        replayed_digest=replayed_digest,
        original_performance=original_perf,
        replayed_performance=replayed_perf,
        original_safety_score=original_safety,
        replayed_safety_score=replayed_safety,
    )


class TestReplayResultProperties:
    def test_digest_unchanged(self) -> None:
        r = _make_result()
        assert r.digest_changed is False

    def test_digest_changed(self) -> None:
        r = _make_result(replayed_digest=_DIGEST_B)
        assert r.digest_changed is True

    def test_performance_delta_positive(self) -> None:
        r = _make_result(original_perf=0.8, replayed_perf=0.9)
        assert r.performance_delta == pytest.approx(0.1)

    def test_performance_delta_negative(self) -> None:
        r = _make_result(original_perf=0.9, replayed_perf=0.8)
        assert r.performance_delta == pytest.approx(-0.1)

    def test_safety_not_degraded(self) -> None:
        r = _make_result(original_safety=0.9, replayed_safety=0.9)
        assert r.safety_degraded is False

    def test_safety_degraded(self) -> None:
        r = _make_result(original_safety=0.9, replayed_safety=0.8)
        assert r.safety_degraded is True

    def test_regression_threshold_no_regression(self) -> None:
        r = _make_result(original_perf=0.8, replayed_perf=0.9)
        assert r.regression_threshold == 0.0

    def test_regression_threshold_with_regression(self) -> None:
        r = _make_result(original_perf=0.9, replayed_perf=0.85)
        assert r.regression_threshold == pytest.approx(0.05)


class TestShadowReplayValidator:
    def setup_method(self) -> None:
        self.validator = ShadowReplayValidator()

    def test_passes_with_stable_digests(self) -> None:
        results = [_make_result(trace_id=f"t{i}") for i in range(3)]
        summary = self.validator.validate(results)
        assert summary.activation_safe is True
        assert summary.all_digests_stable is True

    def test_passes_digest_change_with_improvement(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.8,
            replayed_perf=0.9,
            original_safety=0.9,
            replayed_safety=0.95,
        )
        summary = self.validator.validate([r])
        assert summary.activation_safe is True

    def test_rejects_digest_change_with_no_improvement(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.9,
            replayed_perf=0.8,
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_safety_degradation(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.8,
            replayed_perf=0.95,
            original_safety=0.9,
            replayed_safety=0.7,
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_regression_exceeding_epsilon(self) -> None:
        r = _make_result(
            original_perf=1.0,
            replayed_perf=1.0 - (EPSILON + 0.001),
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_empty_results(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            self.validator.validate([])

    def test_epsilon_is_constant(self) -> None:
        assert isinstance(EPSILON, float)
        assert EPSILON == 0.01

    def test_summary_total_traces(self) -> None:
        results = [_make_result(trace_id=f"t{i}") for i in range(5)]
        summary = self.validator.validate(results)
        assert summary.total_traces == 5
