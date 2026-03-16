"""G-2-6 — Artifact Emission Prohibition for L0/L5/L6.

L0, L5, and L6 MUST NOT emit RESULT or HEALING_PLAN artifacts.
This guard executes at construction-time (not send-time).

Violation raises PermissionError with deterministic message containing:
  - layer
  - artifact type
  - trace_id (if available)
"""

from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "artifact_emission_prohibition_enforcer")
emit_determinism_digest("p0", "artifact_emission_prohibition_enforcer")

_emit_dispatches_healing_run("p1", "artifact_emission_prohibition_enforcer", "L5")
_emit_routes_through("p1", "artifact_emission_prohibition_enforcer", "L5")
_emit_escalates_to_human("p1", "artifact_emission_prohibition_enforcer", "L5")
_emit_reads_policy_state("p1", "artifact_emission_prohibition_enforcer", "L5")
_emit_authorize_and_execute("p2", "artifact_emission_prohibition_enforcer", "execution_auth")
_emit_validates_capability("p2", "artifact_emission_prohibition_enforcer", "capability_check")
_emit_routes_to_capability("p2", "artifact_emission_prohibition_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "artifact_emission_prohibition_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "artifact_emission_prohibition_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "artifact_emission_prohibition_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "artifact_emission_prohibition_enforcer", "exec_output")
_emit_dispatches_agent("p3", "artifact_emission_prohibition_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "artifact_emission_prohibition_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "artifact_emission_prohibition_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "artifact_emission_prohibition_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "artifact_emission_prohibition_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "artifact_emission_prohibition_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "artifact_emission_prohibition_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "artifact_emission_prohibition_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "artifact_emission_prohibition_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "artifact_emission_prohibition_enforcer", "eval_metric")
_emit_stores_embedding("p4", "artifact_emission_prohibition_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "artifact_emission_prohibition_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "artifact_emission_prohibition_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("artifact_emission_prohibition_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("artifact_emission_prohibition_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("artifact_emission_prohibition_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("artifact_emission_prohibition_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("artifact_emission_prohibition_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("artifact_emission_prohibition_enforcer", "p4obs", "alert")
_emit_links_incident_trace("artifact_emission_prohibition_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("artifact_emission_prohibition_enforcer", "p3lm", "pattern")
_emit_records_learning_event("artifact_emission_prohibition_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("artifact_emission_prohibition_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("artifact_emission_prohibition_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("artifact_emission_prohibition_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("artifact_emission_prohibition_enforcer", "p3lm", "policy")
_emit_stores_learning_state("artifact_emission_prohibition_enforcer", "p3lm", "state")
_emit_records_execution_trace("artifact_emission_prohibition_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("artifact_emission_prohibition_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("artifact_emission_prohibition_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("artifact_emission_prohibition_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("artifact_emission_prohibition_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("artifact_emission_prohibition_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("artifact_emission_prohibition_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("artifact_emission_prohibition_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("artifact_emission_prohibition_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "artifact_emission_prohibition_enforcer", "context_pull")
_emit_pulls_context("p1", "artifact_emission_prohibition_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "artifact_emission_prohibition_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "artifact_emission_prohibition_enforcer", "uwg_term_2")
_emit_writes_through("p1", "artifact_emission_prohibition_enforcer", "write_through")
_emit_writes_through("p1", "artifact_emission_prohibition_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "artifact_emission_prohibition_enforcer", "safety_validation")
_emit_invokes_eval("p1", "artifact_emission_prohibition_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "artifact_emission_prohibition_enforcer", "routing_commit")

logger = logging.getLogger(__name__)
FORBIDDEN_EMISSION_LAYERS: frozenset[str] = frozenset({"L0", "L5", "L6"})
FORBIDDEN_ARTIFACT_KINDS: frozenset[str] = frozenset({"RESULT", "HEALING_PLAN"})


def assert_layer_may_emit(artifact_kind: str, layer: str, trace_id: str | None = None) -> None:
    """Fail-closed guard: raises PermissionError if layer may not emit this artifact.

    Args:
        artifact_kind: The artifact type being constructed (e.g. "RESULT", "HEALING_PLAN").
        layer: The calling layer identifier (e.g. "L0", "L2", "L5", "L6").
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_EMISSION_LAYERS and
            artifact_kind is in FORBIDDEN_ARTIFACT_KINDS.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_layer_may_emit", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_layer_may_emit", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "assert_layer_may_emit")
    if layer not in FORBIDDEN_EMISSION_LAYERS:
        return
    if artifact_kind not in FORBIDDEN_ARTIFACT_KINDS:
        return
    msg_parts = [f"ARTIFACT_EMISSION_PROHIBITED:layer={layer}", f"artifact_kind={artifact_kind}"]
    if trace_id is not None:
        msg_parts.append(f"trace_id={trace_id}")
    msg = "|".join(msg_parts)
    logger.error("ARTIFACT_EMISSION_PROHIBITION DENY: %s", msg)
    raise PermissionError(msg)


__all__ = ["FORBIDDEN_ARTIFACT_KINDS", "FORBIDDEN_EMISSION_LAYERS", "assert_layer_may_emit"]
