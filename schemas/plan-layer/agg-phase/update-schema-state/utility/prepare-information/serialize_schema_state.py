"""
Schema definitions for schema state serialization and encoding.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SerializationFormat(Enum):
    """State serialization formats."""
    JSON = "json"
    YAML = "yaml"
    PICKLE = "pickle"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"


class EncodingType(Enum):
    """Data encoding types."""
    UTF_8 = "utf_8"
    UTF_16 = "utf_16"
    ASCII = "ascii"
    BINARY = "binary"


@dataclass
class SerializationConfig:
    """Schema for serialization configuration."""
    format: SerializationFormat
    encoding: EncodingType
    compression: bool = False
    include_metadata: bool = True
    validate_output: bool = True


@dataclass
class SerializedState:
    """Schema for serialized state representation."""
    state_id: str
    format: SerializationFormat
    encoded_data: bytes
    size_bytes: int
    checksum: str
    serialization_timestamp: str


@dataclass
class SerializationResult:
    """Schema for serialization operation results."""
    serialization_id: str
    configuration: SerializationConfig
    serialized_state: SerializedState
    processing_time_ms: int
    original_size_bytes: int