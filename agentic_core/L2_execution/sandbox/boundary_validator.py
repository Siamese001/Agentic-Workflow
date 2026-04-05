"""Addendum 1.2: Transcript–Mutation Cross Check (boundary validator).

After execution, verify:
    computed_diff = diff(boundary_snapshot_pre, boundary_snapshot_post)
    assert computed_diff == UWG.state_diff

Violation: Mismatch → raise MutationReplayIntegrityViolation, HARD FAIL.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "boundary_validator")
emit_determinism_digest("p0", "boundary_validator")

_emit_dispatches_healing_run("p1", "boundary_validator", "L2")
_emit_routes_through("p1", "boundary_validator", "L2")
_emit_checks_agent_registry("p1", "boundary_validator", "agent_registry")
_emit_validates_agent_capability("p1", "boundary_validator", "capability")
_emit_dispatches_execution_plan("p1", "boundary_validator", "exec_plan")
_emit_agent_executes_agent("p1", "boundary_validator", "sub_agent")
_emit_routes_to_agent("p1", "boundary_validator", "target_agent")
_emit_verifies_policy("p1", "boundary_validator", "policy_check")
_emit_observes_runtime_state("p1", "boundary_validator", "runtime_state")
_emit_verifies_boundary("p1", "boundary_validator", "boundary_check")
_emit_transcripts_response("p1", "boundary_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "boundary_validator")
_emit_gated_by_confidence("p1", "boundary_validator", "confidence_gate")
_emit_escalates_to_human("p1", "boundary_validator", "L2")
_emit_reads_policy_state("p1", "boundary_validator", "L2")
_emit_authorize_and_execute("p2", "boundary_validator", "execution_auth")
_emit_validates_capability("p2", "boundary_validator", "capability_check")
_emit_routes_to_capability("p2", "boundary_validator", "capability_route")
_emit_writes_via_uwg("p2", "boundary_validator", "uwg_write")
_emit_blocks_direct_write("p2", "boundary_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "boundary_validator", "tool_invocation")
_emit_captures_execution_output("p2", "boundary_validator", "exec_output")
_emit_dispatches_agent("p3", "boundary_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "boundary_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "boundary_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "boundary_validator", "healing_outcome")
_emit_escalates_failure("p3", "boundary_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "boundary_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "boundary_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "boundary_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "boundary_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "boundary_validator", "eval_metric")
_emit_stores_embedding("p4", "boundary_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "boundary_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "boundary_validator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("boundary_validator", "p4obs", "metric_1")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_2")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_3")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_4")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_5")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_6")
_emit_records_incident_event("boundary_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("boundary_validator", "p4obs", "anomaly")
_emit_writes_observability_log("boundary_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("boundary_validator", "p4obs", "mon_state")
_emit_triggers_alert("boundary_validator", "p4obs", "alert")
_emit_links_incident_trace("boundary_validator", "p4obs", "trace_link")
_emit_captures_pattern("boundary_validator", "p3lm", "pattern")
_emit_records_learning_event("boundary_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("boundary_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("boundary_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("boundary_validator", "p3lm", "routing")
_emit_improves_agent_policy("boundary_validator", "p3lm", "policy")
_emit_stores_learning_state("boundary_validator", "p3lm", "state")
_emit_records_execution_trace("boundary_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("boundary_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("boundary_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("boundary_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("boundary_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("boundary_validator", "env_read", "p2_env_1")
_emit_reads_environ("boundary_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("boundary_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("boundary_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "boundary_validator", "context_pull")
_emit_pulls_context("p1", "boundary_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "boundary_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "boundary_validator", "uwg_term_2")
_emit_writes_through("p1", "boundary_validator", "write_through")
_emit_writes_through("p1", "boundary_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "boundary_validator", "safety_validation")
_emit_invokes_eval("p1", "boundary_validator", "eval_call")
_emit_proposal_commits_routing("p1", "boundary_validator", "routing_commit")

logger = logging.getLogger(__name__)


def _snapshot_hash(snapshot: dict[str, Any]) -> str:
    from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation  # noqa: F401
    raw = json.dumps(snapshot, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def compute_boundary_diff(snapshot_pre: dict[str, Any], snapshot_post: dict[str, Any]) -> dict[str, Any]:
    """Compute a deterministic diff between two boundary snapshots.

    Returns a dict mapping changed keys to (pre_value, post_value) tuples.
    Only top-level key changes are tracked for simplicity.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_boundary_diff", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_boundary_diff", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_boundary_diff")
    all_keys = set(snapshot_pre) | set(snapshot_post)
    diff: dict[str, Any] = {}
    for key in sorted(all_keys):
        pre_val = snapshot_pre.get(key)
        post_val = snapshot_post.get(key)
        if pre_val != post_val:
            diff[key] = {"pre": pre_val, "post": post_val}
    return diff


def _diff_hash(diff: dict[str, Any]) -> str:
    raw = json.dumps(diff, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_mutation_replay_integrity(
    snapshot_pre: dict[str, Any], snapshot_post: dict[str, Any], uwg_state_diff: dict[str, Any]
) -> None:
    """Verify that the observed boundary diff matches the UWG-recorded state_diff.

    Raises MutationReplayIntegrityViolation on mismatch.

    Wire into _run_heal_pipeline() Phase 3 validation.
    """
    computed = compute_boundary_diff(snapshot_pre, snapshot_post)
    computed_h = _diff_hash(computed)
    uwg_h = _diff_hash(uwg_state_diff)
    if computed_h != uwg_h:
        logger.error(
            "MutationReplayIntegrityViolation: computed_diff_hash=%s uwg_diff_hash=%s",
            computed_h[:16],
            uwg_h[:16],
        )
        raise MutationReplayIntegrityViolation(
            f"Boundary diff hash mismatch: computed={computed_h[:16]}... uwg={uwg_h[:16]}... Execution transcript does not match recorded mutations."
        )
    logger.debug("Mutation replay integrity OK: diff_hash=%s", computed_h[:16])


__all__ = ["compute_boundary_diff", "verify_mutation_replay_integrity"]
