from __future__ import annotations
"""Implementation for l4_types."""

import logging

_logger = logging.getLogger(__name__)
# from agentic_core.l4_types_types import *  # Star import removed


# NAMING FIXED: StateError → StateError
class StateError(Exception):
    """Base class for state-related errors."""


# NAMING FIXED: StateValidationError → StateValidationError
class StateValidationError(StateError):
    """Raised when a state transition is invalid."""


# NAMING FIXED: StateRollbackError → StateRollbackError
class StateRollbackError(StateError):
    """Raised when a rollback operation fails."""
