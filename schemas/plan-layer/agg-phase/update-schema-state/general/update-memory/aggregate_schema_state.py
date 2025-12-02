"""
Schema definitions for schema state aggregation and consolidation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class AggregationStrategy(Enum):
    """State aggregation strategies."""
    MERGE = "merge"
    OVERWRITE = "overwrite"
    APPEND = "append"
    TRANSFORM = "transform"


class AggregationScope(Enum):
    """State aggregation scopes."""
    SINGLE_SCHEMA = "single_schema"
    SCHEMA_COLLECTION = "schema_collection"
    LAYER_SPECIFIC = "layer_specific"
    CROSS_LAYER = "cross_layer"


@dataclass
class StateAggregationConfig:
    """Schema for state aggregation configuration."""
    strategy: AggregationStrategy
    scope: AggregationScope
    conflict_resolution: str = "latest_wins"
    preserve_history: bool = True
    aggregation_timestamp: str


@dataclass
class AggregatedState:
    """Schema for aggregated state representation."""
    state_id: str
    source_states: List[str]
    aggregated_data: Dict[str, Any]
    aggregation_metadata: Dict[str, Any]
    version: str


@dataclass
class StateAggregationResult:
    """Schema for state aggregation results."""
    aggregation_id: str
    configuration: StateAggregationConfig
    aggregated_state: AggregatedState
    processing_time_ms: int
    conflicts_resolved: int