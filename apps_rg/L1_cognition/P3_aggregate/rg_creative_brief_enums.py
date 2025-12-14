"""Enum types for rg_creative_brief."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class VoiceType(Enum):
    """Voice type for content generation."""

class ProvenanceStrategy(Enum):
    """Strategy for bullet provenance."""