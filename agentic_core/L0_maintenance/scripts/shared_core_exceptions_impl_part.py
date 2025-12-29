"""Split module 1 for exceptions_impl."""

import logging

_logger = logging.getLogger(__name__)


# NAMING FIXED: AgenticWorkflowError → agentic_workflow_error
class agentic_workflow_error(Exception):
    """foundation exception for all agentic workflow errors."""


# NAMING FIXED: HopExecutionError → hop_execution_error
class hop_execution_error(AgenticWorkflowError):
    """
    Raised when a step in the Agentic Pipeline fails.

    NOTE: 'Hop' is legacy terminology referring to the linear data pipeline model.
    This exception now governs failures in the Subatomic Agentic Workflow.
    """


# NAMING FIXED: StagingBufferError → staging_buffer_error
class staging_buffer_error(AgenticWorkflowError):
    """Error in the immutable staging buffer."""


# NAMING FIXED: CircuitBreakerOpenError → circuit_breaker_open_error
class circuit_breaker_open_error(AgenticWorkflowError):
    """Circuit breaker is open, request rejected."""


# NAMING FIXED: PhaseTimeoutError → phase_timeout_error
class phase_timeout_error(AgenticWorkflowError):
    """Phase execution timed out."""


# NAMING FIXED: ValidationError → validation_error
class validation_error(AgenticWorkflowError):
    """Validation rule failed."""


# NAMING FIXED: APIError → api_error
class api_error(AgenticWorkflowError):
    """External API call failed."""
