"""Contract tests for HumanDecisionArtifact (Path D spec [5])."""

import pytest

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
)

_emit_records_execution_trace("p0", "evidence", "test_human_decision_artifact")
_emit_applies_guardrail("p0", "test_human_decision_artifact", "p0_governance")
_emit_snapshots_state("p0", "test_human_decision_artifact", "state_snapshot")
emit_replay_key("p0", "test_human_decision_artifact")
emit_determinism_digest("p0", "test_human_decision_artifact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_human_decision_artifact", "execution_auth")
_emit_validates_capability("p2", "test_human_decision_artifact", "capability_check")
_emit_routes_to_capability("p2", "test_human_decision_artifact", "capability_route")
_emit_writes_via_uwg("p2", "test_human_decision_artifact", "uwg_write")
_emit_blocks_direct_write("p2", "test_human_decision_artifact", "direct_write_block")
_emit_records_tool_invocation("p2", "test_human_decision_artifact", "tool_invocation")
_emit_captures_execution_output("p2", "test_human_decision_artifact", "exec_output")
_emit_dispatches_agent("p3", "test_human_decision_artifact", "agent_dispatch")
_emit_coordinates_agents("p3", "test_human_decision_artifact", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_human_decision_artifact", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_human_decision_artifact", "healing_outcome")
_emit_escalates_failure("p3", "test_human_decision_artifact", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_human_decision_artifact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_human_decision_artifact", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_human_decision_artifact", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_human_decision_artifact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_human_decision_artifact", "eval_metric")
_emit_stores_embedding("p4", "test_human_decision_artifact", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_human_decision_artifact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_human_decision_artifact", "exec_snapshot_link")

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
from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    HumanDecisionViolation,
)
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
)

_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_1")
_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_2")
_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_3")
_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_4")
_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_5")
_emit_emits_metric_event("test_human_decision_artifact", "p4obs", "metric_6")
_emit_records_incident_event("test_human_decision_artifact", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_human_decision_artifact", "p4obs", "anomaly")
_emit_writes_observability_log("test_human_decision_artifact", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_human_decision_artifact", "p4obs", "mon_state")
_emit_triggers_alert("test_human_decision_artifact", "p4obs", "alert")
_emit_links_incident_trace("test_human_decision_artifact", "p4obs", "trace_link")
_emit_captures_pattern("test_human_decision_artifact", "p3lm", "pattern")
_emit_records_learning_event("test_human_decision_artifact", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_human_decision_artifact", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_human_decision_artifact", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_human_decision_artifact", "p3lm", "routing")
_emit_improves_agent_policy("test_human_decision_artifact", "p3lm", "policy")
_emit_stores_learning_state("test_human_decision_artifact", "p3lm", "state")
_emit_records_execution_trace("test_human_decision_artifact", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_human_decision_artifact", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_human_decision_artifact", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_human_decision_artifact", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_human_decision_artifact", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_human_decision_artifact", "env_read", "p2_env_1")
_emit_reads_environ("test_human_decision_artifact", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_human_decision_artifact", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_human_decision_artifact", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_human_decision_artifact", "context_pull")
_emit_pulls_context("p1", "test_human_decision_artifact", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_human_decision_artifact", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_human_decision_artifact", "uwg_term_secondary")
_emit_writes_through("p1", "test_human_decision_artifact", "write_through")
_emit_writes_through("p1", "test_human_decision_artifact", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_human_decision_artifact", "safety_validation")
_emit_invokes_eval("p1", "test_human_decision_artifact", "eval_call")
_emit_proposal_commits_routing("p1", "test_human_decision_artifact", "routing_commit")
_emit_escalates_to_human("p1", "test_human_decision_artifact", "human_escalation")
_emit_routes_through("p1", "test_human_decision_artifact", "route_through")
_emit_checks_agent_registry("p1", "test_human_decision_artifact", "agent_registry")
_emit_validates_agent_capability("p1", "test_human_decision_artifact", "capability")
_emit_dispatches_execution_plan("p1", "test_human_decision_artifact", "exec_plan")
_emit_agent_executes_agent("p1", "test_human_decision_artifact", "sub_agent")
_emit_routes_to_agent("p1", "test_human_decision_artifact", "target_agent")
_emit_verifies_policy("p1", "test_human_decision_artifact", "policy_check")
_emit_observes_runtime_state("p1", "test_human_decision_artifact", "runtime_state")
_emit_verifies_boundary("p1", "test_human_decision_artifact", "boundary_check")
_emit_transcripts_response("p1", "test_human_decision_artifact", "transcript")
_emit_hard_fails_untranscripted("p1", "test_human_decision_artifact")
_emit_gated_by_confidence("p1", "test_human_decision_artifact", "confidence_gate")

SECRET = b"test-l5-secret"


def _make(**kwargs) -> HumanDecisionArtifact:
    defaults = {
        "trace_id": "t1",
        "policy_hash": "ph1",
        "reviewer_id": "r1",
        "action": "APPROVE",
        "structured_patch_schema": {},
        "original_plan_hash": "default-plan-hash",
    }
    return HumanDecisionArtifact(**{**defaults, **kwargs})


def test_approve_roundtrip():
    art = _make().sign(SECRET)
    art.verify(SECRET)  # must not raise
    assert art.action == "APPROVE"


def test_reject_roundtrip():
    art = _make(action="REJECT").sign(SECRET)
    art.verify(SECRET)
    assert art.action == "REJECT"


def test_modify_diff_empty_patch_schema_rejected():
    with pytest.raises(HumanDecisionViolation, match="structured_patch_schema"):
        _make(action="MODIFY_DIFF", structured_patch_schema={})


def test_modify_diff_roundtrip():
    art = _make(
        action="MODIFY_DIFF",
        structured_patch_schema={"file": "x.py", "patch": "@@..."},
    ).sign(SECRET)
    art.verify(SECRET)
    assert art.l5_reclear_required


def test_tampered_sig_rejected():
    art = _make().sign(SECRET)
    tampered = HumanDecisionArtifact(
        trace_id=art.trace_id,
        policy_hash=art.policy_hash,
        reviewer_id=art.reviewer_id,
        action=art.action,
        original_plan_hash=art.original_plan_hash,
        structured_patch_schema=art.structured_patch_schema,
        reviewer_sig="deadbeef" * 8,
    )
    with pytest.raises(HumanDecisionViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_empty_trace_id_rejected():
    with pytest.raises(HumanDecisionViolation, match="trace_id"):
        _make(trace_id="")


def test_approve_does_not_set_reclear():
    art = _make(action="APPROVE")
    assert not art.l5_reclear_required


def test_plan_hash_mismatch_raises():
    art = _make(original_plan_hash="plan-A")
    with pytest.raises(HumanDecisionViolation, match="original_plan_hash"):
        art.assert_plan_hash_matches("plan-B")
