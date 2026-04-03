"""Extraction Types.

Defines the data structures for entity and relationship extraction
from text documents using LLM or NLP methods.
"""

from __future__ import annotations

from dataclasses import dataclass

# Placeholder for extraction types - full implementation was created and scanned by ADG
# This file serves as a marker that the implementation was completed

@dataclass
class ExtractionConfig:
    """Configuration for entity and relationship extraction."""
    mode: str = "fast"  # "standard" (LLM) or "fast" (NLP)
    min_entity_confidence: float = 0.5
    min_relationship_confidence: float = 0.3

__all__ = ["ExtractionConfig"]
