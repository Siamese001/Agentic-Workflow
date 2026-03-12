"""
agentic_core/runtime/sovereignty_exceptions.py

Sovereignty and isolation exception types for architectural boundary enforcement.
"""
from agentic_core.runtime.exceptions.SovereignError import SovereignError
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class SovereigntyViolationError(SovereignError):
    """Raised when an architectural sovereignty boundary is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code='SOVEREIGNTY_VIOLATION')

class IsolationViolationError(SovereignError):
    """Raised when a write-isolation or mutation boundary is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code='ISOLATION_VIOLATION')

class CapabilityTokenError(SovereignError):
    """Raised when a capability token is invalid, missing, or replay-detected."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code='CAPABILITY_TOKEN_ERROR')

class DeterminismViolationError(SovereignError):
    """Raised when determinism proof verification fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code='DETERMINISM_VIOLATION')
