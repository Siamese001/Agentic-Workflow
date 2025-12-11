"""
Shared module - Core types, configs, and exceptions for all agents.

CANON COMPLIANCE: Centralized shared code, no duplication across agents.
"""

from shared.reasoning_config import ReasoningConfig

__all__ = [
    # Config
    "ContentConstraintsConfig",
    "CONTENT_CONSTRAINTS",
    "SignalControlConfig",
    "SIGNAL_CONTROL",
    # Exceptions
    "AgenticWorkflowError",
    "HopExecutionError",
    "StagingBufferError",
    "CircuitBreakerOpenError",
    "PhaseTimeoutError",
    "ValidationError",
    "APIError",
    # Models
    "ReasoningConfig",
    "ValidationSeverity",
    "ValidationResult",
    "ThematicAnalysis",
    "CircuitState",
    "HopStatus",
    "GateDecision",
    "HopCheckpoint",
    # Reasoning utils
    "reasoning_config_to_api_params",
    "enhance_system_prompt_with_reasoning",
]
