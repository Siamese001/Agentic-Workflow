"""Types and models for error_recovery."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class RecoveryStrategy(Enum):
    RETRY = 'retry'
    FAIL_FAST = 'fail_fast'
    ESCALATE = 'escalate'
    CIRCUIT_BREAK = 'circuit_break'

@dataclass
class ResilienceError:
    """Base descriptor for resilience errors."""
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class TransientError(ResilienceError):
    """Temporary error that may succeed on retry."""
    pass

@dataclass
class PermanentError(ResilienceError):
    """Permanent error that will not succeed on retry."""
    pass

@dataclass
class RetryExhaustedError(ResilienceError):
    """Error indicating all retry attempts have been exhausted."""
    attempts: int = 0
