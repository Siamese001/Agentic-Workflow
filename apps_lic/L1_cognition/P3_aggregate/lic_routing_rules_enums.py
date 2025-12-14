"""Enum types for lic_routing_rules."""
import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class MessageRoute(Enum):
    """Message route types for LinkedIn outreach."""

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""

class SignatureFormat(Enum):
    """Signature format types."""

class CTAFormat(Enum):
    """Call-to-action format types."""