"""Implementation for l4_types."""

import logging

_logger = logging.getLogger(__name__)
# from agentic_core.l4_types_types import *  # Star import removed


# NAMING FIXED: StateError → state_error
class state_error(Exception):
    """Base class for state-related errors."""


# NAMING FIXED: StateValidationError → state_validation_error
class state_validation_error(StateError):
    """Raised when a state transition is invalid."""


# NAMING FIXED: StateRollbackError → state_rollback_error
class state_rollback_error(StateError):
    """Raised when a rollback operation fails."""
