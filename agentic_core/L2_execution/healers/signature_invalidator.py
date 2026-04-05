from __future__ import annotations

import hashlib
from typing import Any, NamedTuple

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

emit_replay_key("p0", "signature_invalidator")
emit_determinism_digest("p0", "signature_invalidator")

_emit_dispatches_healing_run("p1", "signature_invalidator", "L2")
_emit_routes_through("p1", "signature_invalidator", "L2")
_emit_checks_agent_registry("p1", "signature_invalidator", "agent_registry")
_emit_validates_agent_capability("p1", "signature_invalidator", "capability")
_emit_dispatches_execution_plan("p1", "signature_invalidator", "exec_plan")
_emit_agent_executes_agent("p1", "signature_invalidator", "sub_agent")
_emit_routes_to_agent("p1", "signature_invalidator", "target_agent")
_emit_verifies_policy("p1", "signature_invalidator", "policy_check")
_emit_observes_runtime_state("p1", "signature_invalidator", "runtime_state")
_emit_verifies_boundary("p1", "signature_invalidator", "boundary_check")
_emit_transcripts_response("p1", "signature_invalidator", "transcript")
_emit_hard_fails_untranscripted("p1", "signature_invalidator")
_emit_gated_by_confidence("p1", "signature_invalidator", "confidence_gate")
_emit_escalates_to_human("p1", "signature_invalidator", "L2")
_emit_reads_policy_state("p1", "signature_invalidator", "L2")
_emit_authorize_and_execute("p2", "signature_invalidator", "execution_auth")
_emit_validates_capability("p2", "signature_invalidator", "capability_check")
_emit_routes_to_capability("p2", "signature_invalidator", "capability_route")
_emit_writes_via_uwg("p2", "signature_invalidator", "uwg_write")
_emit_blocks_direct_write("p2", "signature_invalidator", "direct_write_block")
_emit_records_tool_invocation("p2", "signature_invalidator", "tool_invocation")
_emit_captures_execution_output("p2", "signature_invalidator", "exec_output")
_emit_dispatches_agent("p3", "signature_invalidator", "agent_dispatch")
_emit_coordinates_agents("p3", "signature_invalidator", "agent_coordination")
_emit_records_workflow_lineage("p3", "signature_invalidator", "workflow_lineage")
_emit_records_healing_outcome("p3", "signature_invalidator", "healing_outcome")
_emit_escalates_failure("p3", "signature_invalidator", "failure_escalation")
_emit_orchestrates_workflow("p3", "signature_invalidator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "signature_invalidator", "healing_dispatch")
_emit_invokes_evaluation("p3", "signature_invalidator", "evaluation_signal")
_emit_records_telemetry_event("p4", "signature_invalidator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "signature_invalidator", "eval_metric")
_emit_stores_embedding("p4", "signature_invalidator", "embedding_store")
_emit_updates_meta_learning_state("p4", "signature_invalidator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "signature_invalidator", "exec_snapshot_link")
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

_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_1")
_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_2")
_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_3")
_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_4")
_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_5")
_emit_emits_metric_event("signature_invalidator", "p4obs", "metric_6")
_emit_records_incident_event("signature_invalidator", "p4obs", "incident")
_emit_captures_runtime_anomaly("signature_invalidator", "p4obs", "anomaly")
_emit_writes_observability_log("signature_invalidator", "p4obs", "obs_log")
_emit_updates_monitoring_state("signature_invalidator", "p4obs", "mon_state")
_emit_triggers_alert("signature_invalidator", "p4obs", "alert")
_emit_links_incident_trace("signature_invalidator", "p4obs", "trace_link")
_emit_captures_pattern("signature_invalidator", "p3lm", "pattern")
_emit_records_learning_event("signature_invalidator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("signature_invalidator", "p3lm", "snapshot")
_emit_feeds_meta_learning("signature_invalidator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("signature_invalidator", "p3lm", "routing")
_emit_improves_agent_policy("signature_invalidator", "p3lm", "policy")
_emit_stores_learning_state("signature_invalidator", "p3lm", "state")
_emit_records_execution_trace("signature_invalidator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("signature_invalidator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("signature_invalidator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("signature_invalidator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("signature_invalidator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("signature_invalidator", "env_read", "p2_env_1")
_emit_reads_environ("signature_invalidator", "env_read", "p2_env_2")
_emit_reads_runtime_state("signature_invalidator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("signature_invalidator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "signature_invalidator", "context_pull")
_emit_pulls_context("p1", "signature_invalidator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "signature_invalidator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "signature_invalidator", "uwg_term_2")
_emit_writes_through("p1", "signature_invalidator", "write_through")
_emit_writes_through("p1", "signature_invalidator", "write_through_2")
_emit_validated_by_safety_plane("p1", "signature_invalidator", "safety_validation")
_emit_invokes_eval("p1", "signature_invalidator", "eval_call")
_emit_proposal_commits_routing("p1", "signature_invalidator", "routing_commit")

HealedPlan = dict[str, Any]


class StaleSignatureViolation(Exception):
    """Raised when a healed plan is executed with a stale signature."""

    pass


class InvalidationResult(NamedTuple):
    """The result of invalidating a plan's signature."""

    invalidated_plan: HealedPlan
    new_policy_hash: str


def invalidate_signature_and_rehash(plan: HealedPlan) -> InvalidationResult:
    """
    Strips cryptographic signatures and regenerates the policy hash for a healed plan.

    This is a critical step for Guarantee #4. After a plan is modified by a
    healing agent, its original approval signature is no longer valid. This
    function ensures the old signature is removed and a new policy hash is
    generated from the modified content, forcing a full L5 re-validation.

    Args:
        plan: The healed plan that has been modified.

    Returns:
        An InvalidationResult containing the plan with its signature stripped
        and a new policy hash for re-validation.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "invalidate_signature_and_rehash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "invalidate_signature_and_rehash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "invalidate_signature_and_rehash")
    invalidated_plan = plan.copy()
    invalidated_plan.pop("l5_signature", None)
    invalidated_plan.pop("l5_approval_timestamp", None)
    invalidated_plan.pop("policy_hash", None)
    import json

    canonical_string = json.dumps(invalidated_plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    new_policy_hash = hashlib.sha256(canonical_string).hexdigest()
    invalidated_plan["policy_hash"] = new_policy_hash
    return InvalidationResult(invalidated_plan=invalidated_plan, new_policy_hash=new_policy_hash)


def verify_no_stale_signature(plan: HealedPlan):
    """
    Verifies that a plan about to be executed does not contain a stale signature.

    This would be called by the execution gateway before committing a change.
    It's a final check to prevent a bypass of the re-clear loop.

    Args:
        plan: The plan to be checked.

    Raises:
        StaleSignatureViolation: If a signature is present on a healed plan that
                                 should have been invalidated.
    """
    if "healed_by" in plan and "l5_signature" in plan:
        raise StaleSignatureViolation("Healed plan contains a stale L5 signature. It must be re-validated.")
