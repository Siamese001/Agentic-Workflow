"""Enum types for lic_routing_rules."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


class MessageRoute(Enum):
    """Message route types for LinkedIn outreach."""


class RecipientArchetype(Enum):
    """Recipient archetype classifications."""


class SignatureFormat(Enum):
    """Signature format types."""


class CTAFormat(Enum):
    """Call-to-action format types."""
