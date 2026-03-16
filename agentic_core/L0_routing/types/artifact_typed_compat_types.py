"""
Backward compatibility stub for artifact_typed_compat module.

This module re-exports symbols from routing_artifact_types
to maintain backwards compatibility with existing imports.

Canonical location: agentic_core/L0_routing/types/routing_artifact_types.py
Compatibility stub: agentic_core/L0_routing/types/artifact_typed_compat_types.py
"""

from __future__ import annotations

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
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "artifact_typed_compat_types")
emit_determinism_digest("p0", "artifact_typed_compat_types")

_emit_dispatches_healing_run("p1", "artifact_typed_compat_types", "L0")
_emit_routes_through("p1", "artifact_typed_compat_types", "L0")
_emit_escalates_to_human("p1", "artifact_typed_compat_types", "L0")
_emit_reads_policy_state("p1", "artifact_typed_compat_types", "L0")

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
