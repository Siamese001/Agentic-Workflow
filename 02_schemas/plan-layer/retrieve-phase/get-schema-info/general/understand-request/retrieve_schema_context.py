"""
Schema definitions for schema context retrieval and extraction.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ContextType(Enum):
    """Types of schema contexts."""
    EXECUTION = "execution"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    DOCUMENTATION = "documentation"


class RetrievalMode(Enum):
    """Context retrieval modes."""
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    CACHED = "cached"
    STREAMING = "streaming"


@dataclass
class ContextQuery:
    """Schema for context retrieval query."""
    query_id: str
    context_type: ContextType
    schema_id: str
    retrieval_mode: RetrievalMode
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class ContextData:
    context_id: str
    context_type: ContextType
    content: Dict[str, Any]
    retrieval_timestamp: str
    metadata: Optional[Dict[str, str]] = None
    """Schema for retrieved context data."""


@dataclass
class ContextRetrievalResult:
    """Schema for context retrieval results."""
    retrieval_id: str
    query: ContextQuery
    context_data: ContextData
    retrieval_time_ms: int
    cache_hit: bool = False