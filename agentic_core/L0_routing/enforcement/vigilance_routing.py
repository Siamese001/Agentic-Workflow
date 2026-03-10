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
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    get_vigilance_severity,
)
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath


def route_vigilance_event(event: Any) -> RoutePath:
    """§Wave4.1 — Deterministic routing from VigilanceEventArtifact tier.

    Returns:
        RoutePath.HUMAN_ESCALATION for HIGH/CRITICAL
        RoutePath.STANDARD_VALIDATION for LOW/MEDIUM
    """
    VigilanceSeverity = get_vigilance_severity()
    if event.vigilance_tier in (VigilanceSeverity.HIGH, VigilanceSeverity.CRITICAL):
        return RoutePath.HUMAN_ESCALATION
    return RoutePath.STANDARD_VALIDATION


__all__ = [
    "route_vigilance_event",
]
