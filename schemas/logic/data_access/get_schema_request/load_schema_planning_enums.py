"""Enum types for load_schema_planning."""

from enum import Enum

class SchemaType(Enum):
    """Types of schemas."""
    JSON = 'json'
    XML = 'xml'
    YAML = 'yaml'
    PROTOBUF = 'protobuf'
    AVRO = 'avro'
    OPENAPI = 'openapi'
    GRAPHQL = 'graphql'

class ValidationMode(Enum):
    """Schema validation modes."""
    STRICT = 'strict'
    LENIENT = 'lenient'
    SYNTAX_ONLY = 'syntax_only'
    DISABLED = 'disabled'

class SchemaScope(Enum):
    """Schema scopes."""
    REQUEST = 'request'
    RESPONSE = 'response'
    EVENT = 'event'
    CONFIG = 'config'
    DATA = 'data'
    INTERNAL = 'internal'

