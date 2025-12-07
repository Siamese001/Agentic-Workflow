"""
03_runtime/compat/models_RES.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 8355aabac02e45cd7e57d5e79510dd995c9e4cc591084e68c411e86b10fd3dcd
"""


from __future__ import annotations

import warnings

# Emit deprecation warning on import
warnings.warn(
    "models_RES is deprecated. Use 'from agentic_workflow.runtime.shared import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all models from the canonical location
from ..shared.models import (
    # Enums
    GateDecision,
    ValidationSeverity,
    ResumeSection,
    JDEnforcementRule,
    BulletProvenance,
    CircuitState,
    HopStatus,
    APICallStatus,
    # Dataclasses
    ReasoningConfig,
    ValidationResult,
    ThematicAnalysis,
    JDEnforcementResult,
    CompetitiveAnalysisConfig,
    RAGMission,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    RAGEvidence,
    RAGCritique,
    RAGState,
    CompetitiveIntelligence,
    RetrievalSource,
    PartialRAGResult,
    RAGTelemetry,
    HopCheckpoint,
    APICallMetrics,
    # Classes
    ImmutableStagingBuffer,
)

# Re-export exceptions that were historically in models_RES
from ..shared.exceptions import (
    HopExecutionError,
    StagingBufferError,
    CircuitBreakerOpenError,
    PhaseTimeoutError,
    FactualFailureException,
    ValidationError,
    ConfigurationError,
    APIError,
)

__all__ = [
    # Enums
    "GateDecision",
    "ValidationSeverity",
    "ResumeSection",
    "JDEnforcementRule",
    "BulletProvenance",
    "CircuitState",
    "HopStatus",
    "APICallStatus",
    # Dataclasses
    "ReasoningConfig",
    "ValidationResult",
    "ThematicAnalysis",
    "JDEnforcementResult",
    "CompetitiveAnalysisConfig",
    "RAGMission",
    "SkillRequirement",
    "SkillCluster",
    "MasterResumeIndex",
    "RAGEvidence",
    "RAGCritique",
    "RAGState",
    "CompetitiveIntelligence",
    "RetrievalSource",
    "PartialRAGResult",
    "RAGTelemetry",
    "HopCheckpoint",
    "APICallMetrics",
    # Classes
    "ImmutableStagingBuffer",
    # Exceptions
    "HopExecutionError",
    "StagingBufferError",
    "CircuitBreakerOpenError",
    "PhaseTimeoutError",
    "FactualFailureException",
    "ValidationError",
    "ConfigurationError",
    "APIError",
]
