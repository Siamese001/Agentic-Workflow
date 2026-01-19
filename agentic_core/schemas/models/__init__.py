from __future__ import annotations
"""
schemas/models – Sovereign Territory

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

# Public API surface — expose only what's intended (lazy imports for healing resilience)
try:
    from .CognitiveContractValidatorSchema import (
        CognitiveContractValidatorSchema,
        CognitiveContract,
        CognitiveContractEnforcer,
        ContractStage,
        Constraint,
        Plan,
        PlanQualityError,
        ConsistencyError,
    )
except ImportError:
    CognitiveContractValidatorSchema = None
    CognitiveContract = None
    CognitiveContractEnforcer = None
    ContractStage = None
    Constraint = None
    Plan = None
    PlanQualityError = None
    ConsistencyError = None

try:
    from .runtime_models import (
        MicroStage,
        HopState,
        RetryPolicy,
        MicroCheckpoint,
        StageTransition,
        InjectionType,
        InjectionScope,
        InjectionPattern,
        InjectionMatch,
        InjectionConfig,
        ValidationResult,
        ExecutionResult,
    )
except ImportError:
    MicroStage = None
    HopState = None
    RetryPolicy = None
    MicroCheckpoint = None
    StageTransition = None
    InjectionType = None
    InjectionScope = None
    InjectionPattern = None
    InjectionMatch = None
    InjectionConfig = None
    ValidationResult = None
    ExecutionResult = None

__all__ = [
    # Cognitive contracts
    "CognitiveContract",
    "CognitiveContractEnforcer",
    "CognitiveContractValidatorSchema",
    "ContractStage",
    "Constraint",
    "Plan",
    "PlanQualityError",
    "ConsistencyError",
    # Runtime models
    "MicroStage",
    "HopState",
    "RetryPolicy",
    "MicroCheckpoint",
    "StageTransition",
    "InjectionType",
    "InjectionScope",
    "InjectionPattern",
    "InjectionMatch",
    "InjectionConfig",
    "ValidationResult",
    "ExecutionResult",
]
