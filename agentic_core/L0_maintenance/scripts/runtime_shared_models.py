"""
RESIDUAL SWEEP COMPLETE: Phase 2C
All models centralized in sovereign SSOT: agentic_core/schemas/models/core_contracts.py

Note: Some models renamed to avoid conflicts:
- AgentMessage -> ResidualAgentMessage
- ValidationResult -> ResidualValidationResult
"""
from agentic_core.schemas.models.core_contracts import (
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
class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""

class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""

class ValidationError(AgenticWorkflowError):
    """Validation error."""

class APIError(AgenticWorkflowError):
    """API-related error."""

class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open."""

__all__ = [
    "LLMResponse", "MessageType", "ResidualAgentMessage", "AgentResponse",
    "ResidualValidationResult", "ReasoningConfig", "HopStatus", "GateDecision",
    "ValidationSeverity", "WorkflowCheckpoint", "ThematicAnalysis", "RAGState",
    "CircuitState", "AgenticWorkflowError", "HopExecutionError", "ValidationError",
    "APIError", "CircuitBreakerOpenError"
]
