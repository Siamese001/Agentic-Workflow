"""Split module 1 for exceptions_impl."""

import logging


logger = logging.getLogger(__name__)


class AgenticWorkflowError(Exception):
    """foundation exception for all agentic workflow errors."""


class HopExecutionError(AgenticWorkflowError):
    """
    Raised when a step in the Agentic Pipeline fails.

    NOTE: 'Hop' is legacy terminology referring to the linear data pipeline model.
    This exception now governs failures in the Subatomic Agentic Workflow.
    """


class StagingBufferError(AgenticWorkflowError):
    """Error in the immutable staging buffer."""


class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open, request rejected."""


class PhaseTimeoutError(AgenticWorkflowError):
    """Phase execution timed out."""


class ValidationError(AgenticWorkflowError):
    """Validation rule failed."""


class APIError(AgenticWorkflowError):
    """External API call failed."""
