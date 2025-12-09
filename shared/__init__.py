"""
Shared module - Core types, configs, and exceptions for all agents.

CANON COMPLIANCE: Centralized shared code, no duplication across agents.
"""

from shared.config import (
    CONTENT_CONSTRAINTS,
    ContentConstraintsConfig,
    SIGNAL_CONTROL,
    SignalControlConfig,
)
from shared.exceptions import (
    AgenticWorkflowError,
    APIError,
    CircuitBreakerOpenError,
    HopExecutionError,
    PhaseTimeoutError,
    StagingBufferError,
    ValidationError,
)
from shared.models import (
    CircuitState,
    GateDecision,
    HopCheckpoint,
    HopStatus,
    ThematicAnalysis,
    ValidationResult,
    ValidationSeverity,
)
from shared.reasoning_config import ReasoningConfig
from shared.reasoning_utils import (
    enhance_system_prompt_with_reasoning,
    reasoning_config_to_api_params,
)

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
