"""
Backward compatibility stub for artifact_typed_compat module.

This module re-exports symbols from routing_artifact_types
to maintain backwards compatibility with existing imports.

Canonical location: agentic_core/L0_routing/types/routing_artifact_types.py
Compatibility stub: agentic_core/L0_routing/types/artifact_typed_compat_types.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.routing_artifact_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AggregateArtifact,
    HealingPlan,
    IncidentArtifact,
    ResultArtifact,
    RouteDecisionArtifact,
    SelfHealingTrigger,
    StaleWriteIncident,
    TokenCapArtifact,
)

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
