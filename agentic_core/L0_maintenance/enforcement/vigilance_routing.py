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

from agentic_core.L0_maintenance.types.v15_types import RoutePath
from agentic_core.L6_observability.types.vigilance_event_types import (
    VigilanceEventArtifact,
    VigilanceSeverity,
)


def route_vigilance_event(event: VigilanceEventArtifact) -> RoutePath:
    """§Wave4.1 — Deterministic routing from VigilanceEventArtifact tier.

    Returns:
        RoutePath.HUMAN_ESCALATION for HIGH/CRITICAL
        RoutePath.STANDARD_VALIDATION for LOW/MEDIUM
    """
    if event.vigilance_tier in (VigilanceSeverity.HIGH, VigilanceSeverity.CRITICAL):
        return RoutePath.HUMAN_ESCALATION
    return RoutePath.STANDARD_VALIDATION


__all__ = [
    "route_vigilance_event",
]
