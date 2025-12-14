"""Types and models for error_recovery."""
import logging



class RecoveryStrategy(Enum):
    """TODO: Add docstring."""


@dataclass
class ResilienceError:
    """Base descriptor for resilience errors."""
    _message: str
    _code: str
    _details: Optional[Dict[str, Any]] = None

@dataclass
class TransientError(ResilienceError):
    """Temporary error that may succeed on retry."""

@dataclass
class PermanentError(ResilienceError):
    """Permanent error that will not succeed on retry."""

@dataclass
class RetryExhaustedError(ResilienceError):
    """Error indicating all retry attempts have been exhausted."""
    _attempts: int = 0
