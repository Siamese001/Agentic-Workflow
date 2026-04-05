"""
Backward compatibility stub for artifact_typed_compat module.

This module re-exports symbols from routing_artifact_types
to maintain backwards compatibility with existing imports.

Canonical location: agentic_core/L0_routing/types/routing_artifact_types.py
Compatibility stub: agentic_core/L0_routing/types/artifact_typed_compat_types.py
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import (
    AggregateArtifact,
    HealingPlan,
    IncidentArtifact,
    ResultArtifact,
    RouteDecisionArtifact,
    SelfHealingTrigger,
    StaleWriteIncident,
    TokenCapArtifact,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_1")
_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_2")
_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_3")
_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_4")
_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_5")
_emit_emits_metric_event("artifact_typed_compat_types", "p4obs", "metric_6")
_emit_records_incident_event("artifact_typed_compat_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("artifact_typed_compat_types", "p4obs", "anomaly")
_emit_writes_observability_log("artifact_typed_compat_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("artifact_typed_compat_types", "p4obs", "mon_state")
_emit_triggers_alert("artifact_typed_compat_types", "p4obs", "alert")
_emit_links_incident_trace("artifact_typed_compat_types", "p4obs", "trace_link")
_emit_captures_pattern("artifact_typed_compat_types", "p3lm", "pattern")
_emit_records_learning_event("artifact_typed_compat_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("artifact_typed_compat_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("artifact_typed_compat_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("artifact_typed_compat_types", "p3lm", "routing")
_emit_improves_agent_policy("artifact_typed_compat_types", "p3lm", "policy")
_emit_stores_learning_state("artifact_typed_compat_types", "p3lm", "state")
_emit_records_execution_trace("artifact_typed_compat_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("artifact_typed_compat_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("artifact_typed_compat_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("artifact_typed_compat_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("artifact_typed_compat_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("artifact_typed_compat_types", "env_read", "p2_env_1")
_emit_reads_environ("artifact_typed_compat_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("artifact_typed_compat_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("artifact_typed_compat_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "artifact_typed_compat_types")
emit_determinism_digest("p0", "artifact_typed_compat_types")

_emit_dispatches_healing_run("p1", "artifact_typed_compat_types", "L0")
_emit_routes_through("p1", "artifact_typed_compat_types", "L0")
_emit_checks_agent_registry("p1", "artifact_typed_compat_types", "agent_registry")
_emit_validates_agent_capability("p1", "artifact_typed_compat_types", "capability")
_emit_dispatches_execution_plan("p1", "artifact_typed_compat_types", "exec_plan")
_emit_agent_executes_agent("p1", "artifact_typed_compat_types", "sub_agent")
_emit_routes_to_agent("p1", "artifact_typed_compat_types", "target_agent")
_emit_verifies_policy("p1", "artifact_typed_compat_types", "policy_check")
_emit_observes_runtime_state("p1", "artifact_typed_compat_types", "runtime_state")
_emit_verifies_boundary("p1", "artifact_typed_compat_types", "boundary_check")
_emit_transcripts_response("p1", "artifact_typed_compat_types", "transcript")
_emit_hard_fails_untranscripted("p1", "artifact_typed_compat_types")
_emit_gated_by_confidence("p1", "artifact_typed_compat_types", "confidence_gate")
_emit_escalates_to_human("p1", "artifact_typed_compat_types", "L0")
_emit_reads_policy_state("p1", "artifact_typed_compat_types", "L0")
_emit_pulls_context("p1", "artifact_typed_compat_types", "context_pull")
_emit_pulls_context("p1", "artifact_typed_compat_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "artifact_typed_compat_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "artifact_typed_compat_types", "uwg_term_secondary")
_emit_writes_through("p1", "artifact_typed_compat_types", "write_through")
_emit_writes_through("p1", "artifact_typed_compat_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "artifact_typed_compat_types", "safety_validation")
_emit_invokes_eval("p1", "artifact_typed_compat_types", "eval_call")
_emit_proposal_commits_routing("p1", "artifact_typed_compat_types", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "artifact_typed_compat_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "artifact_typed_compat_types", "p0_governance")
_emit_snapshots_state("p0", "artifact_typed_compat_types", "state_snapshot")
_emit_authorize_and_execute("p2", "artifact_typed_compat_types", "execution_auth")
_emit_validates_capability("p2", "artifact_typed_compat_types", "capability_check")
_emit_routes_to_capability("p2", "artifact_typed_compat_types", "capability_route")
_emit_writes_via_uwg("p2", "artifact_typed_compat_types", "uwg_write")
_emit_blocks_direct_write("p2", "artifact_typed_compat_types", "direct_write_block")
_emit_records_tool_invocation("p2", "artifact_typed_compat_types", "tool_invocation")
_emit_captures_execution_output("p2", "artifact_typed_compat_types", "exec_output")
_emit_dispatches_agent("p3", "artifact_typed_compat_types", "agent_dispatch")
_emit_coordinates_agents("p3", "artifact_typed_compat_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "artifact_typed_compat_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "artifact_typed_compat_types", "healing_outcome")
_emit_escalates_failure("p3", "artifact_typed_compat_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "artifact_typed_compat_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "artifact_typed_compat_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "artifact_typed_compat_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "artifact_typed_compat_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "artifact_typed_compat_types", "eval_metric")
_emit_stores_embedding("p4", "artifact_typed_compat_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "artifact_typed_compat_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "artifact_typed_compat_types", "exec_snapshot_link")

__all__ = [
    "HealingPlan",
    "IncidentArtifact",
    "ResultArtifact",
    "RouteDecisionArtifact",
    "SelfHealingTrigger",
    "StaleWriteIncident",
    "TokenCapArtifact",
    "AggregateArtifact",
    # TypedDict aliases for backward compatibility
    "HealingPlanTD",
    "IncidentArtifactTD",
    "ResultArtifactTD",
    "StaleWriteIncidentTD",
]

# TypedDict aliases for backward compatibility
HealingPlanTD = dict[str, Any]
IncidentArtifactTD = dict[str, Any]
ResultArtifactTD = dict[str, Any]
StaleWriteIncidentTD = dict[str, Any]
