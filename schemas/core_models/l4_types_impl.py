"""Implementation for l4_types."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class StateError(Exception):
    """Base class for state-related errors."""

class StateValidationError(StateError):
    """Raised when a state transition is invalid."""

class StateRollbackError(StateError):
    """Raised when a rollback operation fails."""