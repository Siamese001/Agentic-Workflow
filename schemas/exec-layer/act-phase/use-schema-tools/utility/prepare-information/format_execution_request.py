"""
Schema definitions for execution request formatting and preparation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class RequestFormat(Enum):
    """Execution request formats."""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    PROTOBUF = "protobuf"


class FormattingStyle(Enum):
    """Request formatting styles."""
    COMPACT = "compact"
    PRETTY = "pretty"
    VERBOSE = "verbose"
    MINIMAL = "minimal"


@dataclass
class RequestFormatConfig:
    """Schema for request format configuration."""
    config_id: str
    request_format: RequestFormat
    formatting_style: FormattingStyle
    include_metadata: bool = True
    compression_enabled: bool = False


@dataclass
class ExecutionRequest:
    """Schema for execution request."""
    request_id: str
    operation_type: str
    target_schema_id: str
    parameters: Dict[str, Any]
    format_config: RequestFormatConfig


@dataclass
class RequestFormattingResult:
    """Schema for request formatting results."""
    result_id: str
    request: ExecutionRequest
    formatted_request: str
    formatting_metadata: Dict[str, Any]