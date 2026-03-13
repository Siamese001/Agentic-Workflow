"""RELOCATED: Config schemas → apps_lic/config/archetype_indicator_config.py (2026-03-11, P1-C).

This file is a backward-compatibility shim for any legacy imports.
Use the canonical config module for new code:
    from apps_lic.config.archetype_indicator_config import AgentSpecs, ArchetypeIndicators
"""

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
