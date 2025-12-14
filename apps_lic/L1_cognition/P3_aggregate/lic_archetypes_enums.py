"""Enum types for lic_archetypes."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""