"""Enum types for models."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: ValidationSeverity → validation_severity
class validation_severity(Enum):
    """Severity levels for validation results."""


# NAMING FIXED: Provider → provider
class provider(str, Enum):
    """Available LLM providers."""


# NAMING FIXED: APICallStatus → api_call_status
class api_call_status(Enum):
    """Status of API calls."""