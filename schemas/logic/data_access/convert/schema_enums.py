"""Enum types for convert_to_internal_schema."""

from enum import Enum

class SchemaType(Enum):
    """Types of schemas supported."""
    JSON_SCHEMA = 'json_schema'
    AVRO = 'avro'
    PROTOBUF = 'protobuf'
    CUSTOM = 'custom'

class ConversionStrategy(Enum):
    """Strategies for schema conversion."""
    STRICT = 'strict'
    LENIENT = 'lenient'
    MAP_ONLY = 'map_only'
    VALIDATE_ONLY = 'validate_only'
