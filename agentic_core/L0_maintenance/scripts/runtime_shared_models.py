"""
RESIDUAL SWEEP COMPLETE: Phase 2C
All models centralized in sovereign SSOT: agentic_core/schemas/models/core_contracts.py

Note: Some models renamed to avoid conflicts:
- AgentMessage -> ResidualAgentMessage
- ValidationResult -> ResidualValidationResult
"""
from agentic_core.schemas.models.core_contracts import (
    LLMResponse,
    MessageType,
    ResidualAgentMessage,
    AgentResponse,
    ResidualValidationResult,
    ReasoningConfig,
    HopStatus,
    GateDecision,
    ValidationSeverity,
    WorkflowCheckpoint,
    ThematicAnalysis,
    RAGState,
    CircuitState,
)

# Exception classes remain here (not schema models)
# NAMING FIXED: AgenticWorkflowError → agentic_workflow_error
class agentic_workflow_error(Exception):
    """Base exception for agentic workflow."""

# NAMING FIXED: HopExecutionError → hop_execution_error
class hop_execution_error(AgenticWorkflowError):
    """Error in hop execution."""

# NAMING FIXED: ValidationError → validation_error
class validation_error(AgenticWorkflowError):
    """Validation error."""

# NAMING FIXED: APIError → api_error
class api_error(AgenticWorkflowError):
    """API-related error."""

# NAMING FIXED: CircuitBreakerOpenError → circuit_breaker_open_error
class circuit_breaker_open_error(AgenticWorkflowError):
    """Circuit breaker is open."""

__all__ = [
    "LLMResponse", "MessageType", "ResidualAgentMessage", "AgentResponse",
    "ResidualValidationResult", "ReasoningConfig", "HopStatus", "GateDecision",
    "ValidationSeverity", "WorkflowCheckpoint", "ThematicAnalysis", "RAGState",
    "CircuitState", "AgenticWorkflowError", "HopExecutionError", "ValidationError",
    "APIError", "CircuitBreakerOpenError"
]
