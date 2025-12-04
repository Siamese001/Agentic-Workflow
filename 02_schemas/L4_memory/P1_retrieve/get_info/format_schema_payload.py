"""
Schema definitions for schema payload formatting and structuring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class PayloadFormat(Enum):
    """Payload formatting options."""
    COMPACT = "compact"
    VERBOSE = "verbose"
    STRUCTURED = "structured"
    FLATTENED = "flattened"


class FormattingStyle(Enum):
    """Payload formatting styles."""
    INDENTED = "indented"
    MINIFIED = "minified"
    PRETTY_PRINT = "pretty_print"
    CUSTOM = "custom"


@dataclass
class PayloadFormattingConfig:
    """Schema for payload formatting configuration."""
    format: PayloadFormat
    style: FormattingStyle
    include_types: bool = True
    include_descriptions: bool = False
    sort_keys: bool = True


@dataclass
class FormattedPayload:
    """Schema for formatted payload representation."""
    payload_id: str
    format: PayloadFormat
    formatted_data: Dict[str, Any]
    size_bytes: int
    formatting_metadata: Dict[str, Any]


@dataclass
class PayloadFormattingResult:
    """Schema for payload formatting results."""
    formatting_id: str
    configuration: PayloadFormattingConfig
    formatted_payload: FormattedPayload
    formatting_time_ms: int
    original_size_bytes: int