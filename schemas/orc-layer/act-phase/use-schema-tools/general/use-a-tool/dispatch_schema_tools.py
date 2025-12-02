"""
Schema definitions for schema tool dispatching and orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ToolCategory(Enum):
    """Schema tool categories."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ANALYSIS = "analysis"
    GENERATION = "generation"


class DispatchStrategy(Enum):
    """Tool dispatch strategies."""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"
    ADAPTIVE = "adaptive"


@dataclass
class ToolDispatch:
    """Schema for individual tool dispatch."""
    dispatch_id: str
    tool_category: ToolCategory
    tool_name: str
    dispatch_strategy: DispatchStrategy
    parameters: Dict[str, Any]
    priority: int = 0


@dataclass
class ToolDispatchContext:
    """Schema for tool dispatch context."""
    context_id: str
    target_schema_id: str
    dispatches: List[ToolDispatch]
    dispatch_environment: Dict[str, Any]
    dispatch_timestamp: str


@dataclass
class ToolDispatchResult:
    """Schema for tool dispatch results."""
    result_id: str
    context: ToolDispatchContext
    dispatch_successful: bool
    dispatched_tools: List[str]
    dispatch_time_ms: int