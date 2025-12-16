"""Enum types for lic_cta_patterns."""
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class RecipientArchetype(Enum):
    """Recipient archetype classifications."""


class CTAStyle(Enum):
    """CTA style types."""

