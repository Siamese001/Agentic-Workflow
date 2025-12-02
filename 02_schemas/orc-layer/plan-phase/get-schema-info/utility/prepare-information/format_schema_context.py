"""
Schema definitions for orchestration-level schema context formatting.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class ContextFormat(Enum):
    """Orchestration context formats."""
    WORKFLOW = "workflow"
    PIPELINE = "pipeline"
    SERVICE_MESH = "service_mesh"
    EVENT_STREAM = "event_stream"


class FormattingLevel(Enum):
    """Context formatting levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ContextFormattingConfig:
    """Schema for context formatting configuration."""
    format: ContextFormat
    level: FormattingLevel
    include_dependencies: bool = True
    include_metadata: bool = True
    include_execution_history: bool = False


@dataclass
class FormattedContext:
    """Schema for formatted orchestration context."""
    context_id: str
    format: ContextFormat
    formatted_data: Dict[str, Any]
    size_bytes: int
    formatting_metadata: Dict[str, Any]


@dataclass
class ContextFormattingResult:
    """Schema for context formatting results."""
    formatting_id: str
    configuration: ContextFormattingConfig
    formatted_context: FormattedContext
    processing_time_ms: int
    original_context_size: int
