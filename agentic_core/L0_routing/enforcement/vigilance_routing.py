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

from agentic_core.L0_routing.enforcement.vigilance_seam import (
    get_vigilance_severity,
)
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


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
