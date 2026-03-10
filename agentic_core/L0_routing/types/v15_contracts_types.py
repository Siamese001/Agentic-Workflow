"""
Backward compatibility stub for v15_contracts_types module.

Canonical location: agentic_core/L0_routing/types/routing_contracts_types.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.routing_contracts_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
