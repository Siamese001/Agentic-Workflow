"""Implementation for l4_types."""


# from .l4_types_types import *  # Star import removed

class StateError(Exception):
    """Base class for state-related errors."""

class StateValidationError(StateError):
    """Raised when a state transition is invalid."""

class StateRollbackError(StateError):
    """Raised when a rollback operation fails."""
