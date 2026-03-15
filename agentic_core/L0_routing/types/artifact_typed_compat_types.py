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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "artifact_typed_compat_types", "L0")
_emit_routes_through("p1", "artifact_typed_compat_types", "L0")
_emit_escalates_to_human("p1", "artifact_typed_compat_types", "L0")
_emit_reads_policy_state("p1", "artifact_typed_compat_types", "L0")

_emit_records_execution_trace("p0", "evidence", "artifact_typed_compat_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "artifact_typed_compat_types", "p0_governance")
_emit_snapshots_state("p0", "artifact_typed_compat_types", "state_snapshot")

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
