"""Tests for rollout & rollback contracts — Wave 7.0.12.

Validates:
  a) rollout requires semantic_clock
  b) CANARY enforces canary_percent bounds; ALL_AT_ONCE forbids canary_percent
  c) invariants must be non-empty
  d) deterministic trace_id with identical inputs
  e) rollback artifact requires semantic_clock and links rollout_trace_id
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)
from agentic_core.L7_meta_learning.types.rollout_types import (
    build_meta_learning_rollback,
    build_meta_learning_rollout_plan,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


def _build_change_package():
    """Build a valid MetaLearningChangePackageArtifact for rollout tests."""
    proposal = build_meta_learning_proposal(
        semantic_clock=_CLOCK,
        proposer="test_subsystem",
        target_component="routing_thresholds",
        before={"threshold": 0.5},
        after={"threshold": 0.7},
        metric_name="accuracy",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="abc123",
        policy_config_hash=None,
    )
    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator="offline_bench",
        dataset_id="ds_001",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="eval_hash",
    )
    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver="human_reviewer",
        decision="APPROVE",
        rationale="Confirmed.",
    )
    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )
    return build_meta_learning_change_package(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        target_component="routing_thresholds",
        change_spec={"threshold": 0.7},
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )


class TestRolloutRequiresSemanticClock:
    def test_rollout_rejects_none_semantic_clock(self) -> None:
        """Rollout plan rejects None semantic_clock."""
        pkg = _build_change_package()
        with pytest.raises(ValueError, match="semantic_clock"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="CANARY",
                canary_percent=10,
                invariants=["guardian_green"],
                max_duration_minutes=60,
                semantic_clock=None,  # type: ignore[arg-type]
            )


class TestCanaryStrategy:
    def test_canary_requires_percent(self) -> None:
        """CANARY strategy requires canary_percent."""
        pkg = _build_change_package()
        with pytest.raises(ValueError, match="CANARY_PERCENT_REQUIRED_FOR_CANARY"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="CANARY",
                canary_percent=None,
                invariants=["guardian_green"],
                max_duration_minutes=60,
                semantic_clock=_CLOCK,
            )

    def test_canary_percent_bounds(self) -> None:
        """CANARY canary_percent must be in [1, 50]."""
        pkg = _build_change_package()
        with pytest.raises(ValueError, match="CANARY_PERCENT_OUT_OF_RANGE"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="CANARY",
                canary_percent=0,
                invariants=["guardian_green"],
                max_duration_minutes=60,
                semantic_clock=_CLOCK,
            )
        with pytest.raises(ValueError, match="CANARY_PERCENT_OUT_OF_RANGE"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="CANARY",
                canary_percent=51,
                invariants=["guardian_green"],
                max_duration_minutes=60,
                semantic_clock=_CLOCK,
            )

    def test_all_at_once_forbids_canary_percent(self) -> None:
        """ALL_AT_ONCE forbids canary_percent."""
        pkg = _build_change_package()
        with pytest.raises(ValueError, match="CANARY_PERCENT_FORBIDDEN_FOR_ALL_AT_ONCE"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="ALL_AT_ONCE",
                canary_percent=10,
                invariants=["guardian_green"],
                max_duration_minutes=60,
                semantic_clock=_CLOCK,
            )


class TestInvariantsNonEmpty:
    def test_invariants_must_be_non_empty(self) -> None:
        """Rollout plan rejects empty invariants."""
        pkg = _build_change_package()
        with pytest.raises(ValueError, match="INVARIANTS_EMPTY"):
            build_meta_learning_rollout_plan(
                pkg,
                strategy="ALL_AT_ONCE",
                invariants=[],
                max_duration_minutes=60,
                semantic_clock=_CLOCK,
            )


class TestRolloutDeterminism:
    def test_deterministic_trace_id(self) -> None:
        """Identical inputs produce identical trace_id and JSON."""
        pkg = _build_change_package()
        r1 = build_meta_learning_rollout_plan(
            pkg,
            strategy="CANARY",
            canary_percent=10,
            invariants=["guardian_green", "no_metric_regression"],
            max_duration_minutes=120,
            semantic_clock=_CLOCK,
        )
        r2 = build_meta_learning_rollout_plan(
            pkg,
            strategy="CANARY",
            canary_percent=10,
            invariants=["guardian_green", "no_metric_regression"],
            max_duration_minutes=120,
            semantic_clock=_CLOCK,
        )
        assert r1.trace_id == r2.trace_id
        assert r1.to_json() == r2.to_json()
        assert len(r1.trace_id) == 64
        assert r1.change_package_trace_id == pkg.trace_id


class TestRollbackArtifact:
    def test_rollback_requires_semantic_clock(self) -> None:
        """Rollback rejects None semantic_clock."""
        pkg = _build_change_package()
        rollout = build_meta_learning_rollout_plan(
            pkg,
            strategy="ALL_AT_ONCE",
            invariants=["guardian_green"],
            max_duration_minutes=30,
            semantic_clock=_CLOCK,
        )
        with pytest.raises(ValueError, match="semantic_clock"):
            build_meta_learning_rollback(
                rollout,
                rollback_reason="INVARIANT_VIOLATION",
                semantic_clock=None,  # type: ignore[arg-type]
            )

    def test_rollback_links_rollout_trace_id(self) -> None:
        """Rollback trace_id is deterministic and links to rollout."""
        pkg = _build_change_package()
        rollout = build_meta_learning_rollout_plan(
            pkg,
            strategy="ALL_AT_ONCE",
            invariants=["guardian_green"],
            max_duration_minutes=30,
            semantic_clock=_CLOCK,
        )
        rb1 = build_meta_learning_rollback(
            rollout,
            rollback_reason="METRIC_REGRESSION",
            semantic_clock=_CLOCK,
        )
        rb2 = build_meta_learning_rollback(
            rollout,
            rollback_reason="METRIC_REGRESSION",
            semantic_clock=_CLOCK,
        )
        assert rb1.rollout_trace_id == rollout.trace_id
        assert rb1.trace_id == rb2.trace_id
        assert rb1.to_json() == rb2.to_json()
        assert rb1.rollback_reason == "METRIC_REGRESSION"
