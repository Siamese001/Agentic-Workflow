"""
Schema definitions for schema payload preparation and formatting.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class PayloadFormat(Enum):
    """Supported payload formats."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    BINARY = "binary"


class CompressionType(Enum):
    """Payload compression types."""
    NONE = "none"
    GZIP = "gzip"
    ZSTD = "zstd"
    LZ4 = "lz4"


@dataclass
class SchemaPayload:
    """Schema for prepared schema payload."""
    payload_id: str
    format: PayloadFormat
    compression: CompressionType
    size_bytes: int
    checksum: str
    metadata: Optional[Dict[str, str]] = None


@dataclass
class PayloadConfiguration:
    """Schema for payload preparation configuration."""
    target_format: PayloadFormat
    compression: CompressionType
    include_metadata: bool = True
    validate_integrity: bool = True


@dataclass
class PreparedPayload:
    """Schema for completely prepared payload."""
    payload: SchemaPayload
    configuration: PayloadConfiguration
    preparation_timestamp: str
    expires_at: Optional[str] = None