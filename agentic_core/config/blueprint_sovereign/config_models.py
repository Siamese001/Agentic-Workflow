"""
DEPRECATED – Phase 5 Comprehensive Enforcement Sweep (Dec 26, 2025)
All models have been migrated to the Sovereign SSOT:
AgenticCore/schemas/models/core_contracts.py

This file now serves as a backward-compatible import proxy.
New code MUST import directly from core_contracts.py
"""
from AgenticCore.schemas.models.core_contracts import (
    FilePathsConfig,
    ArtistConfig,
    ValidatorConfig,
    PromptsConfig,
    WebRagConfig,
    EnricherConfig,
    EnforcementRAGConfig as RAGConfig,  # Aliased for backward compatibility
    EnforcementReasoningConfig as ReasoningConfig,  # Aliased for backward compatibility
    ContentConstraintsConfig,
    SignalControlConfig,
    PromptAddendumConfig,
    AppConfig,
)

__all__ = [
    "FilePathsConfig",
    "ArtistConfig",
    "ValidatorConfig",
    "PromptsConfig",
    "WebRagConfig",
    "EnricherConfig",
    "RAGConfig",
    "ReasoningConfig",
    "ContentConstraintsConfig",
    "SignalControlConfig",
    "PromptAddendumConfig",
    "AppConfig",
]
