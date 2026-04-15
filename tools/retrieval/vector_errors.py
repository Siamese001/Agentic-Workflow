"""Typed exceptions for the vector retrieval service."""

from __future__ import annotations


class VectorServiceError(RuntimeError):
    """Base error for retrieval-service failures."""


class VectorValidationError(VectorServiceError):
    """User input or request-shape error."""


class VectorUnavailableError(VectorServiceError):
    """Backend or model is not ready or not reachable."""


class VectorConflictError(VectorServiceError):
    """Requested create/upsert action conflicts with current state."""


class VectorNotFoundError(VectorServiceError):
    """Requested collection or resource does not exist."""


class VectorConfigurationError(VectorServiceError):
    """Configuration is invalid for the requested action."""
