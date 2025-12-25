"""Enum types for rg_creative_brief."""
from enum import Enum, auto
import logging

_logger = logging.getLogger(__name__)


class VoiceType(Enum):
    """Voice type for content generation."""


class ProvenanceStrategy(Enum):
    """Strategy for bullet provenance."""
