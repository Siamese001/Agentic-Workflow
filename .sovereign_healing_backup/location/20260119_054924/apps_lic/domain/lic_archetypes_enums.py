from __future__ import annotations
"""Enum types for lic_archetypes."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: RecipientArchetype → RecipientArchetype
class RecipientArchetype(Enum):
    """Recipient Archetype classifications."""