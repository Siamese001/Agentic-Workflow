from __future__ import annotations

"\nRESIDUAL SWEEP COMPLETE: Phase 2C\nAll models centralized in sovereign SSOT: agentic_core/runtime/types/core_contracts_types.py\n\nNote: Some models renamed to avoid conflicts:\n- AgentMessage -> ResidualAgentMessage\n- ValidationResult -> ResidualValidationResult\n"
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


class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""


class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""


class ValidationError(AgenticWorkflowError):
    """Validation error."""


class ApiError(AgenticWorkflowError):
    """API-related error."""


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
