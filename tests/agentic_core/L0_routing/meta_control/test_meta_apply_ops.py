"""Tests for meta-learning operational boundaries — Wave 7.0.15.

Validates:
  a) Invariant failure triggers rollback (files restored).
  b) Rate limit blocks second apply within window.
  c) CANARY requires percent and records canary state deterministically.
  d) Rollback artifact trace determinism.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.meta_control.meta_apply import (
    _atomic_write_json,
    _config_path,
)
from agentic_core.L0_routing.meta_control.meta_apply_ops import (
    apply_with_invariants,
    check_rate_limit,
    record_apply_timestamp,
    record_canary_state,
    rollback_meta_learning_rollout,
)
from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)
from agentic_core.L7_meta_learning.types.rollout_types import (
    build_meta_learning_rollout_plan,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


def _build_pipeline(
    *,
    target_component: str = "routing_thresholds",
    change_spec: dict | None = None,
    strategy: str = "ALL_AT_ONCE",
    canary_percent: int | None = None,
    invariants: list[str] | None = None,
    policy_config_hash: str | None = None,
):
    """Build a full pipeline returning (change_package, rollout_plan)."""
    spec = change_spec if change_spec is not None else {"threshold": 0.05}
    invs = invariants if invariants is not None else ["no_schema_changes"]

    proposal = build_meta_learning_proposal(
        semantic_clock=_CLOCK,
        proposer="test_subsystem",
        target_component=target_component,
        before={"threshold": 0.5},
        after=spec,
        metric_name="accuracy",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="abc123",
        policy_config_hash=policy_config_hash,
    )
    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator="offline_bench",
        dataset_id="ds_001",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="eval_hash",
        policy_config_hash=policy_config_hash,
    )
    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver="human_reviewer",
        decision="APPROVE",
        rationale="Confirmed.",
        policy_config_hash=policy_config_hash,
    )
    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=_CLOCK,
        policy_config_hash=policy_config_hash,
    )
    change_package = build_meta_learning_change_package(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        target_component=target_component,
        change_spec=spec,
        semantic_clock=_CLOCK,
        policy_config_hash=policy_config_hash,
    )
    rollout_plan = build_meta_learning_rollout_plan(
        change_package,
        strategy=strategy,
        canary_percent=canary_percent,
        invariants=invs,
        max_duration_minutes=60,
        semantic_clock=_CLOCK,
        policy_config_hash=policy_config_hash,
    )
    return change_package, rollout_plan


class TestInvariantFailureRollback:
    def test_invariant_failure_triggers_rollback(self, tmp_path: Path) -> None:
        """When invariant fails, prior config is restored."""
        pkg, rollout = _build_pipeline(
            invariants=["guardian_determinism_empty_diff"],
        )

        # Pre-populate existing config
        comp_dir = tmp_path / "routing_thresholds"
        comp_dir.mkdir(parents=True)
        config_file = comp_dir / "config.json"
        _atomic_write_json(config_file, {"threshold": 0.01})

        # Inject failure marker for guardian_determinism_empty_diff
        (comp_dir / ".guardian_diff_fail").write_text("fail", encoding="utf-8")

        result = apply_with_invariants(
            change_package_trace_id=pkg.trace_id,
            rollout_plan=rollout,
            change_spec=pkg.change_spec,
            target_component="routing_thresholds",
            base_dir=tmp_path,
            semantic_clock=_CLOCK,
        )

        assert result.outcome == "REJECTED"
        assert "INVARIANT_VIOLATION" in result.reject_reason

        # Config should be restored to prior value
        restored = json.loads(config_file.read_text(encoding="utf-8"))
        assert restored == {"threshold": 0.01}

    def test_invariant_pass_keeps_new_config(self, tmp_path: Path) -> None:
        """When all invariants pass, new config is kept."""
        pkg, rollout = _build_pipeline(
            invariants=["no_schema_changes", "policy_hash_unchanged"],
        )

        result = apply_with_invariants(
            change_package_trace_id=pkg.trace_id,
            rollout_plan=rollout,
            change_spec=pkg.change_spec,
            target_component="routing_thresholds",
            base_dir=tmp_path,
            semantic_clock=_CLOCK,
        )

        assert result.outcome == "APPLIED"
        config_file = _config_path(tmp_path, "routing_thresholds")
        data = json.loads(config_file.read_text(encoding="utf-8"))
        assert data == {"threshold": 0.05}


class TestRateLimiter:
    def test_rate_limit_blocks_second_apply(self, tmp_path: Path) -> None:
        """Second apply within 1 hour is blocked."""
        now = 1_000_000
        record_apply_timestamp(tmp_path, "apps_rg", "routing_thresholds", now)

        allowed, last = check_rate_limit(tmp_path, "apps_rg", "routing_thresholds", now + 1800)
        assert not allowed
        assert last == now

    def test_rate_limit_allows_after_window(self, tmp_path: Path) -> None:
        """Apply after 1 hour window is allowed."""
        now = 1_000_000
        record_apply_timestamp(tmp_path, "apps_rg", "routing_thresholds", now)

        allowed, _ = check_rate_limit(tmp_path, "apps_rg", "routing_thresholds", now + 3601)
        assert allowed

    def test_rate_limit_different_app_id(self, tmp_path: Path) -> None:
        """Different app_id is not rate limited."""
        now = 1_000_000
        record_apply_timestamp(tmp_path, "apps_rg", "routing_thresholds", now)

        allowed, _ = check_rate_limit(tmp_path, "apps_lic", "routing_thresholds", now + 100)
        assert allowed


class TestCanaryGovernance:
    def test_canary_records_state_deterministically(self, tmp_path: Path) -> None:
        """CANARY rollout records canary state file."""
        _, rollout = _build_pipeline(
            strategy="CANARY",
            canary_percent=10,
            invariants=["no_schema_changes"],
        )

        state1 = record_canary_state(
            rollout_plan=rollout, target_component="routing_thresholds", base_dir=tmp_path
        )
        state2 = record_canary_state(
            rollout_plan=rollout, target_component="routing_thresholds", base_dir=tmp_path
        )

        assert state1 == state2
        assert state1["strategy"] == "CANARY"
        assert state1["canary_percent"] == 10

        canary_file = tmp_path / "routing_thresholds" / "canary_state.json"
        assert canary_file.exists()
        persisted = json.loads(canary_file.read_text(encoding="utf-8"))
        assert persisted["canary_percent"] == 10

    def test_canary_rejects_non_canary_strategy(self, tmp_path: Path) -> None:
        """record_canary_state rejects non-CANARY strategy."""
        _, rollout = _build_pipeline(strategy="ALL_AT_ONCE")
        with pytest.raises(ValueError, match="CANARY"):
            record_canary_state(
                rollout_plan=rollout, target_component="routing_thresholds", base_dir=tmp_path
            )


class TestRollbackDeterminism:
    def test_rollback_artifact_trace_determinism(self, tmp_path: Path) -> None:
        """Same rollback inputs produce identical trace_id."""
        _, rollout = _build_pipeline()

        # Create config + rollback files
        comp_dir = tmp_path / "routing_thresholds"
        comp_dir.mkdir(parents=True)
        _atomic_write_json(comp_dir / "config.json", {"threshold": 0.05})
        _atomic_write_json(comp_dir / "rollback.json", {"threshold": 0.01})

        rb1 = rollback_meta_learning_rollout(
            rollout_plan=rollout,
            reason="METRIC_REGRESSION",
            target_component="routing_thresholds",
            base_dir=tmp_path,
            semantic_clock=_CLOCK,
        )
        rb2 = rollback_meta_learning_rollout(
            rollout_plan=rollout,
            reason="METRIC_REGRESSION",
            target_component="routing_thresholds",
            base_dir=tmp_path,
            semantic_clock=_CLOCK,
        )
        assert rb1.trace_id == rb2.trace_id
        assert len(rb1.trace_id) == 64
        assert rb1.rollback_reason == "METRIC_REGRESSION"
        assert rb1.rollout_trace_id == rollout.trace_id
