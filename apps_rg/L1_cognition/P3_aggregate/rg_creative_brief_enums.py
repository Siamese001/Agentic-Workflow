"""Enum types for rg_creative_brief."""
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class VoiceType(Enum):
    """Voice type for content generation."""


class ProvenanceStrategy(Enum):
    """Strategy for bullet provenance."""

