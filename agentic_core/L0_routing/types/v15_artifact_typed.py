"""
Backward compatibility stub for v15_artifact_typed module.

This module re-exports symbols from v15_artifact_types
to maintain backwards compatibility with existing imports.

Canonical location: agentic_core/L0_routing/types/v15_artifact_types.py
Compatibility stub: agentic_core/L0_routing/types/v15_artifact_typed.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.v15_artifact_types import (
    AggregateArtifactTD,
    HealingPlanTD,
    IncidentArtifactTD,
    ResultArtifactTD,
    RouteDecisionArtifactTD,
    SelfHealingTriggerTD,
    StaleWriteIncidentTD,
    TokenCapArtifactTD,
)

__all__ = [
    "HealingPlanTD",
    "IncidentArtifactTD",
    "ResultArtifactTD",
    "RouteDecisionArtifactTD",
    "SelfHealingTriggerTD",
    "StaleWriteIncidentTD",
    "TokenCapArtifactTD",
    "AggregateArtifactTD",
]
