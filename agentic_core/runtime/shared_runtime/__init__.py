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
from .reflection_engine import ReflectionEngine, CritiqueResult, ValidationCriterion, ReflectionConfig, MutationRequest
from .signal_enhancer import SignalEnhancer, SignalQuality, SignalAssessment, QualityThresholds, ClaimAnalysis

__all__ = [
    "ReflectionEngine",
    "CritiqueResult",
    "ValidationCriterion",
    "ReflectionConfig",
    "MutationRequest",
    "SignalEnhancer",
    "SignalQuality",
    "SignalAssessment",
    "QualityThresholds",
    "ClaimAnalysis",
]
