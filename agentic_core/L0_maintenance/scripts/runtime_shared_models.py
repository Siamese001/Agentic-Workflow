from __future__ import annotations
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
    "LLMResponse", "MessageType", "ResidualAgentMessage", "AgentResponse",
    "ResidualValidationResult", "ReasoningConfig", "HopStatus", "GateDecision",
    "ValidationSeverity", "WorkflowCheckpoint", "ThematicAnalysis", "RAGState",
    "CircuitState", "AgenticWorkflowError", "HopExecutionError", "ValidationError",
    "APIError", "CircuitBreakerOpenError"
]
