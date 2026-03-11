from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
RESIDUAL SWEEP COMPLETE: Phase 2C
All models centralized in sovereign SSOT: agentic_core/runtime/types/core_contracts_types.py

Note: Some models renamed to avoid conflicts:
- AgentMessage -> ResidualAgentMessage
- ValidationResult -> ResidualValidationResult
"""
from agentic_core.runtime.types.core_contracts_types import (
    AgentResponse,
    CircuitState,
    GateDecision,
    HopStatus,
    LLMResponse,
    MessageType,
    RAGState,
    ReasoningConfig,
    ResidualAgentMessage,
    ResidualValidationResult,
    ThematicAnalysis,
    ValidationSeverity,
    WorkflowCheckpoint,
)


# Exception classes remain here (not schema models)
# NAMING FIXED: AgenticWorkflowError → AgenticWorkflowError
class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""


# NAMING FIXED: HopExecutionError → HopExecutionError
class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""


# NAMING FIXED: ValidationError → ValidationError
class ValidationError(AgenticWorkflowError):
    """Validation error."""


# NAMING FIXED: APIError → ApiError
class ApiError(AgenticWorkflowError):
    """API-related error."""


# NAMING FIXED: CircuitBreakerOpenError → CircuitBreakerOpenError
class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open."""


__all__ = [
    "LLMResponse",
    "MessageType",
    "ResidualAgentMessage",
    "AgentResponse",
    "ResidualValidationResult",
    "ReasoningConfig",
    "HopStatus",
    "GateDecision",
    "ValidationSeverity",
    "WorkflowCheckpoint",
    "ThematicAnalysis",
    "RAGState",
    "CircuitState",
    "AgenticWorkflowError",
    "HopExecutionError",
    "ValidationError",
    "ApiError",
    "CircuitBreakerOpenError",
]
