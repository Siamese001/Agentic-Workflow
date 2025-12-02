"""
Schema definitions for schema context formatting and structuring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class ContextType(Enum):
    """Types of schema contexts."""
    EXECUTION = "execution"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    DOCUMENTATION = "documentation"


class FormattingStyle(Enum):
    """Context formatting styles."""
    COMPACT = "compact"
    VERBOSE = "verbose"
    STRUCTURED = "structured"
    FLAT = "flat"


@dataclass
class SchemaContext:
    """Schema for formatted schema context."""
    context_id: str
    context_type: ContextType
    formatting_style: FormattingStyle
    content: Dict[str, Any]
    hierarchy_level: int


@dataclass
class ContextFormattingRules:
    """Schema for context formatting rules."""
    include_inheritance: bool = True
    max_depth: int = 10
    sort_keys: bool = True
    preserve_order: bool = False


@dataclass
class FormattedContext:
    """Schema for completely formatted context."""
    context: SchemaContext
    formatting_rules: ContextFormattingRules
    formatted_output: Dict[str, Any]
    formatting_timestamp: str