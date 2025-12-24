from enum import Enum
"""Enum types for models."""
from enum import Enum, auto

import logging

_logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation results."""


class Provider(str, Enum):
    """Available LLM providers."""


class APICallStatus(Enum):
    """Status of API calls."""