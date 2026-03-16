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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
