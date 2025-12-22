"""L1 Cognition Layer

Provides cognitive capabilities for agent autonomy including
episodic memory and reasoning systems.
"""
import re

import logging

LOGGER = logging.getLogger(__name__)

try:
    from agentic_core.L1_cognition.episodic_memory import Episode, EpisodicMemory
except Exception as e:
    LOGGER.debug(f"EpisodicMemory not available: {e}")
    Episode = None
    EpisodicMemory = None

def create_episodic_memory(*args, **kwargs):
    """Factory function for EpisodicMemory."""
    if EpisodicMemory is None:
        raise ImportError("EpisodicMemory not available")
    return EpisodicMemory(*args, **kwargs)

__all__ = [
    "Episode",
    "EpisodicMemory",
    "create_episodic_memory",
]
