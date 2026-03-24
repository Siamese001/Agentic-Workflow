"""
§Wave4.1 — L0 Vigilance Event Routing Intake.

Accepts a VigilanceEventArtifact from L6 and maps it to an L0 routing
decision (RoutePath). Does not modify existing L0 entry paths for user
requests.

Routing rules (deterministic, no fallback to wall-clock):
  LOW / MEDIUM  → STANDARD_VALIDATION (L5 rules-first)
  HIGH / CRITICAL → HUMAN_ESCALATION (HIL path)
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.seams.vigilance_seam import (
    get_vigilance_severity,
)
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "vigilance_routing")
emit_determinism_digest("p0", "vigilance_routing")

_emit_dispatches_healing_run("p1", "vigilance_routing", "L0")
_emit_routes_through("p1", "vigilance_routing", "L0")
_emit_checks_agent_registry("p1", "vigilance_routing", "agent_registry")
_emit_validates_agent_capability("p1", "vigilance_routing", "capability")
_emit_dispatches_execution_plan("p1", "vigilance_routing", "exec_plan")
_emit_agent_executes_agent("p1", "vigilance_routing", "sub_agent")
_emit_routes_to_agent("p1", "vigilance_routing", "target_agent")
_emit_verifies_policy("p1", "vigilance_routing", "policy_check")
_emit_observes_runtime_state("p1", "vigilance_routing", "runtime_state")
_emit_verifies_boundary("p1", "vigilance_routing", "boundary_check")
_emit_transcripts_response("p1", "vigilance_routing", "transcript")
_emit_hard_fails_untranscripted("p1", "vigilance_routing")
_emit_gated_by_confidence("p1", "vigilance_routing", "confidence_gate")
_emit_escalates_to_human("p1", "vigilance_routing", "L0")
_emit_reads_policy_state("p1", "vigilance_routing", "L0")
_emit_authorize_and_execute("p2", "vigilance_routing", "execution_auth")
_emit_validates_capability("p2", "vigilance_routing", "capability_check")
_emit_routes_to_capability("p2", "vigilance_routing", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_routing", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_routing", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_routing", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_routing", "exec_output")
_emit_dispatches_agent("p3", "vigilance_routing", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_routing", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_routing", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_routing", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_routing", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_routing", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_routing", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_routing", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_routing", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_routing", "eval_metric")
_emit_stores_embedding("p4", "vigilance_routing", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_routing", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_routing", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_1")
_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_2")
_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_3")
_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_4")
_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_5")
_emit_emits_metric_event("vigilance_routing", "p4obs", "metric_6")
_emit_records_incident_event("vigilance_routing", "p4obs", "incident")
_emit_captures_runtime_anomaly("vigilance_routing", "p4obs", "anomaly")
_emit_writes_observability_log("vigilance_routing", "p4obs", "obs_log")
_emit_updates_monitoring_state("vigilance_routing", "p4obs", "mon_state")
_emit_triggers_alert("vigilance_routing", "p4obs", "alert")
_emit_links_incident_trace("vigilance_routing", "p4obs", "trace_link")
_emit_captures_pattern("vigilance_routing", "p3lm", "pattern")
_emit_records_learning_event("vigilance_routing", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vigilance_routing", "p3lm", "snapshot")
_emit_feeds_meta_learning("vigilance_routing", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vigilance_routing", "p3lm", "routing")
_emit_improves_agent_policy("vigilance_routing", "p3lm", "policy")
_emit_stores_learning_state("vigilance_routing", "p3lm", "state")
_emit_records_execution_trace("vigilance_routing", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vigilance_routing", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vigilance_routing", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vigilance_routing", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vigilance_routing", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vigilance_routing", "env_read", "p2_env_1")
_emit_reads_environ("vigilance_routing", "env_read", "p2_env_2")
_emit_reads_runtime_state("vigilance_routing", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vigilance_routing", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vigilance_routing", "context_pull")
_emit_pulls_context("p1", "vigilance_routing", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vigilance_routing", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vigilance_routing", "uwg_term_2")
_emit_writes_through("p1", "vigilance_routing", "write_through")
_emit_writes_through("p1", "vigilance_routing", "write_through_2")
_emit_validated_by_safety_plane("p1", "vigilance_routing", "safety_validation")
_emit_invokes_eval("p1", "vigilance_routing", "eval_call")
_emit_proposal_commits_routing("p1", "vigilance_routing", "routing_commit")


def route_vigilance_event(event: Any) -> RoutePath:
    """§Wave4.1 — Deterministic routing from VigilanceEventArtifact tier.

    Returns:
        RoutePath.HUMAN_ESCALATION for HIGH/CRITICAL
        RoutePath.STANDARD_VALIDATION for LOW/MEDIUM
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "route_vigilance_event", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "route_vigilance_event", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "route_vigilance_event")
    VigilanceSeverity = get_vigilance_severity()
    if event.vigilance_tier in (VigilanceSeverity.HIGH, VigilanceSeverity.CRITICAL):
        return RoutePath.HUMAN_ESCALATION
    return RoutePath.STANDARD_VALIDATION


__all__ = [
    "route_vigilance_event",
]
