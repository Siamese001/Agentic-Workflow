"""Enum types for models."""
import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation results."""

class Provider(str, Enum):
    """Available LLM providers."""

class APICallStatus(Enum):
    """Status of API calls."""