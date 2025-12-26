"""
DEPRECATED – Phase 5 Comprehensive Enforcement Sweep (Dec 26, 2025)
All models have been migrated to the Sovereign SSOT:
agentic_core/schemas/models/core_contracts.py

This file now serves as a backward-compatible import proxy.
New code MUST import directly from core_contracts.py

NOTE: This file contained duplicate models (ValidationResult, ThematicAnalysis, RAGState)
that were already in core_contracts.py from Phase 2C. Only new models were migrated.
"""
from agentic_core.schemas.models.core_contracts import (
    ValidationResult,
    ThematicAnalysis,
    APICallMetrics,
    RAGState,
    ImmutableStagingBuffer,
)

__all__ = [
    "ValidationResult",
    "ThematicAnalysis",
    "APICallMetrics",
    "RAGState",
    "ImmutableStagingBuffer",
]
