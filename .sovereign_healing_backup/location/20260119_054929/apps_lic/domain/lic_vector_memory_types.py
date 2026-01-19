from __future__ import annotations
"""Types and models for lic_vector_memory."""
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


@dataclass
# NAMING FIXED: VectorDocument → VectorDocument
class VectorDocument:
    """Document stored in vector memory."""

    _id: str
    _text: str
    _metadata: Dict[str, object]
    _embedding: Optional[List[float]] = None
    _distance: Optional[float] = None


@dataclass
# NAMING FIXED: QueryResult → QueryResult
class QueryResult:
    """Result from a vector memory query."""

    _documents: List[VectorDocument]
    _total_count: int
    _query_text: str
    _query_time_ms: float = 0.0


@dataclass
# NAMING FIXED: MemoryStats → MemoryStats
class MemoryStats:
    """Statistics about the vector memory store."""

    _collection_name: str
    _document_count: int
    _persist_directory: str