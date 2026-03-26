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

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_meta_learning_rollout")
# REMOVED: _emit_applies_guardrail("p0", "test_meta_learning_rollout", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_meta_learning_rollout", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_meta_learning_rollout", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_meta_learning_rollout")
# REMOVED: emit_determinism_digest("p0", "test_meta_learning_rollout")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_meta_learning_rollout", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_meta_learning_rollout", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_meta_learning_rollout", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_meta_learning_rollout", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_meta_learning_rollout", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_meta_learning_rollout", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_meta_learning_rollout", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_meta_learning_rollout", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_meta_learning_rollout", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_meta_learning_rollout", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_meta_learning_rollout", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_meta_learning_rollout", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_meta_learning_rollout", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_meta_learning_rollout", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_meta_learning_rollout", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_meta_learning_rollout", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_meta_learning_rollout", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_meta_learning_rollout", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_meta_learning_rollout", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_meta_learning_rollout", "exec_snapshot_link")

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

    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_meta_learning_rollout", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_meta_learning_rollout", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_meta_learning_rollout", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_meta_learning_rollout", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_meta_learning_rollout", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_meta_learning_rollout", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_meta_learning_rollout", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_meta_learning_rollout", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_meta_learning_rollout", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_meta_learning_rollout", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_meta_learning_rollout", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_meta_learning_rollout", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_meta_learning_rollout", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_meta_learning_rollout", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_meta_learning_rollout", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_meta_learning_rollout", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_meta_learning_rollout", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_meta_learning_rollout", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_meta_learning_rollout", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_meta_learning_rollout", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_meta_learning_rollout", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_rollout", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_rollout", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_rollout", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_rollout", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_rollout", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_rollout", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_rollout", "write_through")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_rollout", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_meta_learning_rollout", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_meta_learning_rollout", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_meta_learning_rollout", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_meta_learning_rollout", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_meta_learning_rollout", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_meta_learning_rollout", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_meta_learning_rollout", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_meta_learning_rollout", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_meta_learning_rollout", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_meta_learning_rollout", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_meta_learning_rollout", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_meta_learning_rollout", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_meta_learning_rollout", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_meta_learning_rollout", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_meta_learning_rollout")
# REMOVED: _emit_gated_by_confidence("p1", "test_meta_learning_rollout", "confidence_gate")

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
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
            _emit_agent_executes_agent,
            _emit_applies_guardrail,  # noqa: E402
            _emit_authorize_and_execute,
            _emit_blocks_direct_write,
            _emit_captures_evaluation_metric,
            _emit_captures_execution_output,
            _emit_checks_agent_registry,
            _emit_coordinates_agents,
            _emit_dispatches_agent,
            _emit_dispatches_execution_plan,
            _emit_dispatches_healing_run,
            _emit_escalates_failure,
            _emit_escalates_to_human,
            _emit_gated_by_confidence,
            _emit_hard_fails_untranscripted,
            _emit_invokes_evaluation,
            _emit_links_execution_to_snapshot,
            _emit_observes_runtime_state,
            _emit_orchestrates_workflow,
            _emit_reads_policy_state,  # noqa: E402
            _emit_records_execution_trace,  # noqa: E402
            _emit_records_healing_outcome,
            _emit_records_telemetry_event,
            _emit_records_tool_invocation,
            _emit_records_workflow_lineage,
            _emit_routes_through,
            _emit_routes_to_agent,
            _emit_routes_to_capability,
            _emit_signs_execution_trace,  # noqa: E402
            _emit_snapshots_state,  # noqa: E402
            _emit_stores_embedding,
            _emit_transcripts_response,
            _emit_updates_meta_learning_state,
            _emit_validates_agent_capability,
            _emit_validates_capability,
            _emit_verifies_boundary,
            _emit_verifies_policy,
            _emit_writes_via_uwg,
            emit_determinism_digest,  # noqa: E402
            emit_replay_key,  # noqa: E402
        from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
            _emit_agent_executes_agent,
            _emit_captures_pattern,
            _emit_captures_runtime_anomaly,
            _emit_checks_agent_registry,
            _emit_dispatches_execution_plan,
            _emit_emits_metric_event,
            _emit_escalates_to_human,
            _emit_execution_terminates_at_uwg,
            _emit_feeds_meta_learning,
            _emit_gated_by_confidence,
            _emit_hard_fails_untranscripted,
            _emit_improves_agent_policy,
            _emit_invokes_eval,
            _emit_links_incident_trace,  # noqa: E402
            _emit_observes_runtime_state,
            _emit_proposal_commits_routing,
            _emit_pulls_context,
            _emit_reads_environ,
            _emit_reads_runtime_state,
            _emit_records_execution_trace,
            _emit_records_incident_event,
            _emit_records_learning_event,
            _emit_routes_through,
            _emit_routes_to_agent,
            _emit_stores_learning_state,
            _emit_transcripts_response,
            _emit_triggers_alert,
            _emit_updates_monitoring_state,
            _emit_updates_routing_strategy,
            _emit_validated_by_safety_plane,
            _emit_validates_agent_capability,
            _emit_verifies_boundary,
            _emit_verifies_policy,
            _emit_writes_learning_snapshot,
            _emit_writes_observability_log,
            _emit_writes_through,  # noqa: E402
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
