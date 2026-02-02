from __future__ import annotations

"""
runtime/shared_runtime – Sovereign Territory

Purpose:
    Sovereign territory

Best Practices:
    - Single responsibility per module
    - Explicit imports only from approved layers (gravity compliance)
    - All public functions/classes fully typed and documented
    - No side effects unless explicitly in L2_execution or L4_state
    - No raw strings — use prompt_governance for prompts
    - No inline Pydantic models — use schemas/models

Current Status (December 28, 2025):
    - Territory claimed and protected
    - Awaiting sovereign curation of high-signal implementations

Future Curation Roadmap:
    - Implement canonical patterns for this layer
    - Add unit + property + stateful tests
    - Register with relevant L4/L5 systems
"""

# Public API surface — expose only what's intended
# Graceful imports - some modules may not exist yet
try:
    from .reflection_engine import (
        CritiqueResult,
        MutationRequest,
        ReflectionConfig,
        ReflectionEngine,
        ValidationCriterion,
    )
except ImportError:
    ReflectionEngine = None
    CritiqueResult = None
    ValidationCriterion = None
    ReflectionConfig = None
    MutationRequest = None

try:
    from .signal_enhancer import (
        ClaimAnalysis,
        QualityThresholds,
        SignalAssessment,
        SignalQuality,
        signal_enhancer,
    )
except ImportError:
    signal_enhancer = None
    SignalQuality = None
    SignalAssessment = None
    QualityThresholds = None
    ClaimAnalysis = None

# AST Validator base class - DEPRECATED: CanonASTValidator removed
# from .ast_validator import CanonASTValidator, parse_and_validate

__all__ = [
    "ReflectionEngine",
    "CritiqueResult",
    "ValidationCriterion",
    "ReflectionConfig",
    "MutationRequest",
    "signal_enhancer",
    "SignalQuality",
    "SignalAssessment",
    "QualityThresholds",
    "ClaimAnalysis",
    "CanonASTValidator",
    "parse_and_validate",
]
