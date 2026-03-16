"""
Backward compatibility stub for v15_contracts_types module.

Canonical location: agentic_core/L0_routing/types/routing_contracts_types.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.routing_contracts_types import (
    RESULT_EMISSION_ALLOWED_LAYERS,
    ArtifactAbsenceFailure,
    GuardrailGuard,
    HealingTransactionBoundary,
    LawSlotHandler,
    MetaGuardianResult,
    PipeOrderEnforcer,
    PipeOrderViolation,
    PolicyAlignmentResult,
    PolicyConfigGuard,
    PolicyMutationIncident,
    ResultEmissionViolation,
    RouteRecoveryBox,
    TelemetryEmitter,
    TieredVigilanceMonitor,
    aggregate_gate_check,
    enforce_artifact_presence,
    enforce_route_decision_presence,
    meta_guardian_check,
    static_policy_alignment_check,
    validate_result_emission,
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

emit_replay_key("p0", "v15_contracts_types")
emit_determinism_digest("p0", "v15_contracts_types")

_emit_dispatches_healing_run("p1", "v15_contracts_types", "L0")
_emit_routes_through("p1", "v15_contracts_types", "L0")
_emit_escalates_to_human("p1", "v15_contracts_types", "L0")
_emit_reads_policy_state("p1", "v15_contracts_types", "L0")

_emit_records_execution_trace("p0", "evidence", "v15_contracts_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "v15_contracts_types", "p0_governance")
_emit_snapshots_state("p0", "v15_contracts_types", "state_snapshot")
_emit_authorize_and_execute("p2", "v15_contracts_types", "execution_auth")
_emit_validates_capability("p2", "v15_contracts_types", "capability_check")
_emit_routes_to_capability("p2", "v15_contracts_types", "capability_route")
_emit_writes_via_uwg("p2", "v15_contracts_types", "uwg_write")
_emit_blocks_direct_write("p2", "v15_contracts_types", "direct_write_block")
_emit_records_tool_invocation("p2", "v15_contracts_types", "tool_invocation")
_emit_captures_execution_output("p2", "v15_contracts_types", "exec_output")
_emit_dispatches_agent("p3", "v15_contracts_types", "agent_dispatch")
_emit_coordinates_agents("p3", "v15_contracts_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "v15_contracts_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "v15_contracts_types", "healing_outcome")
_emit_escalates_failure("p3", "v15_contracts_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "v15_contracts_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "v15_contracts_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "v15_contracts_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "v15_contracts_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "v15_contracts_types", "eval_metric")
_emit_stores_embedding("p4", "v15_contracts_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "v15_contracts_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "v15_contracts_types", "exec_snapshot_link")

__all__ = [
    "ArtifactAbsenceFailure",
    "GuardrailGuard",
    "HealingTransactionBoundary",
    "LawSlotHandler",
    "MetaGuardianResult",
    "PipeOrderEnforcer",
    "PipeOrderViolation",
    "PolicyAlignmentResult",
    "PolicyConfigGuard",
    "PolicyMutationIncident",
    "RESULT_EMISSION_ALLOWED_LAYERS",
    "ResultEmissionViolation",
    "RouteRecoveryBox",
    "TelemetryEmitter",
    "TieredVigilanceMonitor",
    "aggregate_gate_check",
    "enforce_artifact_presence",
    "enforce_route_decision_presence",
    "meta_guardian_check",
    "static_policy_alignment_check",
    "validate_result_emission",
]
