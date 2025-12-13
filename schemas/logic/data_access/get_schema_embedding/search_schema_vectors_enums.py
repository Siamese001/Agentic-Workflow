"""Enum types for search_schema_vectors."""

from enum import Enum

class SchemaSearchMode(Enum):
    """Search modes for schema vector operations."""
    SEMANTIC = 'semantic'
    STRUCTURAL = 'structural'
    HYBRID = 'hybrid'
    FIELD_BASED = 'field_based'

class SchemaSimilarityType(Enum):
    """Types of schema similarity."""
    STRUCTURAL = 'structural'
    SEMANTIC = 'semantic'
    FIELD_OVERLAP = 'field_overlap'
    TYPE_COMPATIBILITY = 'type_compatibility'
