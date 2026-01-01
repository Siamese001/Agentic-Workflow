"""Enum types for lic_cta_patterns."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: RecipientArchetype → recipient_archetype
class recipient_archetype(Enum):
    """Recipient archetype classifications."""


# NAMING FIXED: CTAStyle → cta_style
class cta_style(Enum):
    """CTA style types."""