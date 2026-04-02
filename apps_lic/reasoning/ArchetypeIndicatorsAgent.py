"""RELOCATED: Config schemas → apps_lic/config/archetype_indicator_config.py (2026-03-11, P1-C).

DEPRECATED: This shim will be removed in a future release.
Import from the canonical config module directly:
    from apps_lic.config.archetype_indicator_config import AgentSpecs, ArchetypeIndicators

This file is a backward-compatibility shim for any legacy imports.
"""

import warnings

warnings.warn(
    "ArchetypeIndicatorsAgent is deprecated. Import from apps_lic.config.archetype_indicator_config directly.",
    DeprecationWarning,
    stacklevel=2,
)

from apps_lic.config.archetype_indicator_config import (
    AgentSpecs,
    ArchetypeIndicators,
    Conditions,
    Constraints,
    FallbackRAGParams,
    GateDecisionAgent,
    GenerationAgent,
    ProfileAnalysisAgent,
    QAReportAgent,
    ResearchAgent,
    RoutingAgent,
    RoutingRule,
    ScoringWeights,
    SenderGroundingAgent,
    ValidationAgent,
    VectorStoreQueryParams,
)

__all__ = [
    "AgentSpecs",
    "ArchetypeIndicators",
    "Conditions",
    "Constraints",
    "FallbackRAGParams",
    "GateDecisionAgent",
    "GenerationAgent",
    "ProfileAnalysisAgent",
    "QAReportAgent",
    "ResearchAgent",
    "RoutingAgent",
    "RoutingRule",
    "ScoringWeights",
    "SenderGroundingAgent",
    "ValidationAgent",
    "VectorStoreQueryParams",
]
