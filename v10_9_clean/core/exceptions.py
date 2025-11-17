"""Custom exceptions for the v10_7 runtime layer."""
from __future__ import annotations


class RuntimeConfigurationError(Exception):
    """Raised when configuration validation fails."""


class ModelClientError(Exception):
    """Raised when an LLM client invocation fails."""


class ValidationError(Exception):
    """Raised when response validation does not pass."""


class BudgetExceededError(Exception):
    """Raised when a context budget is exhausted."""


class CacheMiss(Exception):
    """Raised to indicate a semantic cache miss when required."""
