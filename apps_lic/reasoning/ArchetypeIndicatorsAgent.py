"""RELOCATED: Config schemas → apps_lic/config/archetype_indicator_config.py (2026-03-11, P1-C).

This file is a backward-compatibility shim for any legacy imports.
Use the canonical config module for new code:
    from apps_lic.config.archetype_indicator_config import AgentSpecs, ArchetypeIndicators
"""

from apps_lic.config.archetype_indicator_config import (  # noqa: F401
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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
