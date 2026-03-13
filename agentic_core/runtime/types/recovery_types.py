from __future__ import annotations

"Types and models for error_recovery."
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

_logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """TODO: Add docstring."""


@dataclass
class ResilienceError:
    """Base descriptor for resilience errors."""

    _message: str
    _code: str
    _details: dict[str, Any] | None = None


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
