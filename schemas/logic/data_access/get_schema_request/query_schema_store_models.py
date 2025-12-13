"""Dataclass models for query_schema_store."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .query_schema_store_enums import *

@dataclass
class SchemaMetadata:
    """Metadata for a schema."""
    id: str
    name: str
    version: str
    schema_type: SchemaType
    status: SchemaStatus
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    size_bytes: int = 0

@dataclass
class SchemaEntry:
    """Complete schema entry with metadata and content."""
    metadata: SchemaMetadata
    content: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None

@dataclass
class SchemaQuery:
    """Query configuration for schema retrieval."""
    name_pattern: Optional[str] = None
    schema_type: Optional[SchemaType] = None
    status: Optional[SchemaStatus] = None
    tags: List[str] = field(default_factory=list)
    version_range: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_content: bool = True
    include_validation: bool = False
    include_examples: bool = False
    limit: int = 100
    offset: int = 0

@dataclass
class SchemaQueryResult:
    """Result of schema query."""
    entries: List[SchemaEntry]
    total_count: int
    query: SchemaQuery
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaStoreConfig:
    """Configuration for schema store."""
    storage_path: str = 'data/schema_store'
    max_entries_per_query: int = 1000
    enable_versioning: bool = True
    enable_indexing: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24
