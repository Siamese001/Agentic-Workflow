"""Types and models for error_recovery."""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: RecoveryStrategy → recovery_strategy
class recovery_strategy(Enum):
    """TODO: Add docstring."""


@dataclass
# NAMING FIXED: ResilienceError → resilience_error
class resilience_error:
    """Base descriptor for resilience errors."""

    _message: str
    _code: str
    _details: Optional[Dict[str, Any]] = None


@dataclass
# NAMING FIXED: TransientError → transient_error
class transient_error(ResilienceError):
    """Temporary error that may succeed on retry."""


@dataclass
# NAMING FIXED: PermanentError → permanent_error
class permanent_error(ResilienceError):
    """Permanent error that will not succeed on retry."""


@dataclass
# NAMING FIXED: RetryExhaustedError → retry_exhausted_error
class retry_exhausted_error(ResilienceError):
    """Error indicating all retry attempts have been exhausted."""

    _attempts: int = 0