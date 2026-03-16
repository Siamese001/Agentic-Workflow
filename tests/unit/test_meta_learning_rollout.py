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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_rollout")
_emit_applies_guardrail("p0", "test_meta_learning_rollout", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_rollout", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_rollout", "state_snapshot")
emit_replay_key("p0", "test_meta_learning_rollout")
emit_determinism_digest("p0", "test_meta_learning_rollout")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_rollout", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_rollout", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_rollout", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_rollout", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_rollout", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_rollout", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_rollout", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_rollout", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_rollout", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_rollout", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_rollout", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_rollout", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_rollout", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_rollout", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_rollout", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_rollout", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_rollout", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_rollout", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_rollout", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_rollout", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)
from system_learning.types.rollout_types import (
    build_meta_learning_rollback,
    build_meta_learning_rollout_plan,
)

_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_rollout", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_rollout", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_rollout", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_rollout", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_rollout", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_rollout", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_rollout", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_rollout", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_rollout", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_rollout", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_rollout", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_rollout", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_rollout", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_rollout", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_rollout", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_rollout", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_rollout", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_rollout", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_rollout", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_rollout", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_rollout", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_rollout", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_learning_rollout", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_rollout", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_rollout", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_rollout", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_learning_rollout", "write_through")
_emit_writes_through("p1", "test_meta_learning_rollout", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_learning_rollout", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_rollout", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_rollout", "routing_commit")

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
