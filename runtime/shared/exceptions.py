"""
Runtime shared exceptions.
"""

class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""
    pass

class HopExecutionError(AgenticWorkflowError):
    """Error during hop execution."""
    pass

class ValidationError(AgenticWorkflowError):
    """Error during validation."""
    pass

class APIError(AgenticWorkflowError):
    """Error during API calls."""
    pass

class CircuitBreakerOpenError(AgenticWorkflowError):
    """Error when circuit breaker is open."""
    pass

class StagingBufferError(AgenticWorkflowError):
    """Error in staging buffer operations."""
    pass
