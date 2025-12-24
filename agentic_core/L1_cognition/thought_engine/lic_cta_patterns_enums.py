"""Enum types for lic_cta_patterns."""
from enum import Enum, auto


import logging

_logger = logging.getLogger(__name__)


class RecipientArchetype(Enum):
    """Recipient archetype classifications."""


class CTAStyle(Enum):
    """CTA style types."""
