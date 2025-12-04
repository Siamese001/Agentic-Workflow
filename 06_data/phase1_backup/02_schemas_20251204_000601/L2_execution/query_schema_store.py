"""
Schema definitions for schema store querying and search operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class QueryType(Enum):
    """Types of schema store queries."""
    SEARCH = "search"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"


class QueryLanguage(Enum):
    """Supported query languages."""
    SQL = "sql"
    GRAPHQL = "graphql"
    SPARQL = "sparql"
    CUSTOM_DSL = "custom_dsl"


@dataclass
class QueryParameters:
    """Schema for query execution parameters."""
    query_type: QueryType
    language: QueryLanguage
    query_string: str
    parameters: Dict[str, Any]
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class QueryResult:
    """Schema for individual query result."""
    result_id: str
    data: List[Dict[str, Any]]
    total_count: int
    execution_time_ms: int
    has_more: bool = False


@dataclass
class StoreQuery:
    query_id: str
    store_name: str
    parameters: QueryParameters
    execution_metadata: Dict[str, Any]
    result: Optional[QueryResult] = None
    """Schema for complete store query."""