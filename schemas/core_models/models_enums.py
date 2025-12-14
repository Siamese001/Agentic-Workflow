"""Enum types for models."""
import logging



class ValidationSeverity(Enum):
    """Severity levels for validation results."""

class Provider(str, Enum):
    """Available LLM providers."""

class APICallStatus(Enum):
    """Status of API calls."""
