"""
Schema definitions for parsing schema configuration settings.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class SchemaFormat(Enum):
    """Supported schema format types."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    PROTOBUF = "protobuf"


class ValidationMode(Enum):
    """Schema validation modes."""
    STRICT = "strict"
    LENIENT = "lenient"
    DISABLED = "disabled"


@dataclass
class SchemaSettings:
    """Schema for configuration settings."""
    schema_format: SchemaFormat
    validation_mode: ValidationMode
    max_depth: int
    allow_extensions: bool = False
    custom_validators: Optional[List[str]] = None


@dataclass
class ParsingConfiguration:
    """Schema for parsing configuration parameters."""
    encoding: str = "utf-8"
    strip_whitespace: bool = True
    preserve_comments: bool = False
    error_on_unknown_fields: bool = True


@dataclass
class SchemaParseRequest:
    """Schema for parse request parameters."""
    settings: SchemaSettings
    configuration: ParsingConfiguration
    target_schema_id: str
    source_data: Optional[Dict[str, Any]] = None