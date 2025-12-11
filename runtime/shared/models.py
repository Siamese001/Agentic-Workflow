"""
Re-export shim for runtime.shared.models

This module re-exports everything from shared.models and apps_shared.rag.hardening.models
to maintain backward compatibility for the compatibility layer.
"""

# Re-export everything from shared.models
from shared.models import *

# Re-export specific types from apps_shared.rag.hardening.models
# Note: Only import types, not the full module to avoid circular imports
from apps_shared.rag.hardening.models import (
    ResumeSection,
    JDEnforcementRule,
    BulletProvenance,
    JDEnforcementResult,
    CompetitiveAnalysisConfig,
    RAGMission,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    RAGEvidence,
    RAGCritique,
    CompetitiveIntelligence,
    RetrievalSource,
    PartialRAGResult,
    RAGTelemetry,
)
