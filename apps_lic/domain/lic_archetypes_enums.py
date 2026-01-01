"""Enum types for lic_archetypes."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: RecipientArchetype → recipient_archetype
class recipient_archetype(Enum):
    """Recipient archetype classifications."""