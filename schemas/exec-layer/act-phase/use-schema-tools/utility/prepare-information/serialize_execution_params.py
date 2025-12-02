"""
Schema definitions for execution parameter serialization and encoding.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SerializationFormat(Enum):
    """Execution parameter serialization formats."""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    BINARY = "binary"


class EncodingType(Enum):
    """Parameter encoding types."""
    UTF8 = "utf8"
    BASE64 = "base64"
    HEX = "hex"
    COMPRESSED = "compressed"


@dataclass
class SerializationConfig:
    """Schema for serialization configuration."""
    config_id: str
    serialization_format: SerializationFormat
    encoding_type: EncodingType
    include_type_info: bool = True
    compress_output: bool = False


@dataclass
class ExecutionParameters:
    """Schema for execution parameters."""
    parameters_id: str
    parameter_data: Dict[str, Any]
    config: SerializationConfig
    validation_rules: List[Dict[str, Any]]


@dataclass
class SerializationResult:
    """Schema for serialization results."""
    result_id: str
    parameters: ExecutionParameters
    serialized_data: str
    serialization_successful: bool
    serialization_time_ms: int