"""
Backward compatibility stub for artifact_validate_compat module.

This module re-exports symbols from artifact_validate_compat_types
to maintain backwards compatibility with existing imports.

Canonical location: agentic_core/L0_routing/types/artifact_validators_types.py
Compatibility stub: agentic_core/L0_routing/types/artifact_validate_compat_types.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.artifact_validators_types import (
    make_healing_plan_from_dataclass,
    make_result_artifact_from_dataclass,
    to_healing_plan_dict,
    to_incident_artifact_dict,
    to_result_artifact_dict,
    to_stale_write_incident_dict,
    validate_healing_plan,
    validate_incident_artifact,
    validate_result_artifact,
    validate_stale_write_incident,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "artifact_validate_compat_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "artifact_validate_compat_types", "p0_governance")
_emit_snapshots_state("p0", "artifact_validate_compat_types", "state_snapshot")

__all__ = [
    "make_healing_plan_from_dataclass",
    "make_result_artifact_from_dataclass",
    "to_healing_plan_dict",
    "to_incident_artifact_dict",
    "to_result_artifact_dict",
    "to_stale_write_incident_dict",
    "validate_healing_plan",
    "validate_incident_artifact",
    "validate_result_artifact",
    "validate_stale_write_incident",
]
