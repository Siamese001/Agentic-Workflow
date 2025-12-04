"""
Schema definitions for schema state querying and retrieval.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class StateType(Enum):
    """Schema state types."""
    CURRENT_STATE = "current_state"
    HISTORICAL_STATE = "historical_state"
    PROJECTED_STATE = "projected_state"
    AGGREGATE_STATE = "aggregate_state"


class QueryMode(Enum):
    """Schema query modes."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class StateQuery:
    """Schema for state query."""
    query_id: str
    state_type: StateType
    query_mode: QueryMode
    target_schema_id: str
    query_parameters: Dict[str, Any]


@dataclass
class StateRetrieval:
    """Schema for state retrieval operation."""
    retrieval_id: str
    query: StateQuery
    retrieval_timestamp: str
    retrieval_strategy: str


@dataclass
class StateQueryResult:
    """Schema for state query results."""
    result_id: str
    retrieval: StateRetrieval
    state_data: Dict[str, Any]
    query_successful: bool
    state_metadata: Dict[str, Any]