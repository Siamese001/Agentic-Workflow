"""Schema Types and Data Models - Core definitions for schema operations.


logger = logging.getLogger(__name__)
This module contains all enum types and dataclass definitions used across
schema planning and orchestration operations.
"""

from typing import Dict, List, Optional, Any
import logging

class SchemaType(Enum):
    """Types of schemas for different data formats."""
    JSON = "json"
    XML = "xml"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    SQL = "sql"
    YAML = "yaml"

class ValidationLevel(Enum):
    """Levels of schema validation."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    BUSINESS = "business"
    FULL = "full"

class TransformationType(Enum):
    """Types of schema transformations."""
    FORMAT_CONVERSION = "format_conversion"
    FIELD_MAPPING = "field_mapping"
    TYPE_COERCION = "type_coercion"
    STRUCTURE_REFACTOR = "structure_refactor"
    VERSION_MIGRATION = "version_migration"

@dataclass
class SchemaDefinition:
    """Definition of a data schema."""
    name: str
    schema_type: SchemaType
    version: str
    content: Dict[str, Any]
    namespace: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class ValidationRule:
    """Rule for schema validation."""
    name: str
    rule_type: ValidationLevel
    condition: str
    message: str
    severity: str = "error"
