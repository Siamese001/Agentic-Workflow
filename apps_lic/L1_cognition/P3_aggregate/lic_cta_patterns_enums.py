"""Enum types for lic_cta_patterns."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""

class CTAStyle(Enum):
    """CTA style types."""