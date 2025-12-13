"""Dataclass models for search_schema_vectors."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
# from .search_schema_vectors_enums import *  # Star import removed

@dataclass
class SchemaVectorEntry:
    """Entry in the schema vector store."""
    schema_id: str
    schema_name: str
    vector: List[float]
    field_vectors: Dict[str, List[float]] = field(default_factory=dict)
    schema_type: str = 'json'
    field_count: int = 0
    complexity_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaSearchQuery:
    """Search query for schema vectors."""
    query_text: Optional[str] = None
    query_schema: Optional[Dict[str, Any]] = None
    query_vector: Optional[List[float]] = None
    search_mode: SchemaSearchMode = SchemaSearchMode.SEMANTIC
    similarity_type: SchemaSimilarityType = SchemaSimilarityType.SEMANTIC
    top_k: int = 10
    threshold: float = 0.7
    schema_type_filter: Optional[str] = None
    min_field_overlap: int = 0
    include_field_matches: bool = False

@dataclass
class SchemaSearchResult:
    """Result of schema vector search."""
    entries: List[SchemaVectorEntry]
    scores: List[float]
    field_matches: Optional[List[Dict[str, Any]]] = None
    search_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaVectorConfig:
    """Configuration for schema vector operations."""
    dimension: int = 1536
    enable_field_vectors: bool = True
    similarity_threshold: float = 0.7
    max_entries: int = 10000
    index_type: str = 'hnsw'
