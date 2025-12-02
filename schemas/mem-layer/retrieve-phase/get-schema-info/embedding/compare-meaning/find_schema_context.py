"""
Schema definitions for schema context finding and discovery.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union, Tuple
from enum import Enum


class ContextType(Enum):
    """Schema context types."""
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"


class DiscoveryMethod(Enum):
    """Context discovery methods."""
    PATTERN_MATCHING = "pattern_matching"
    SIMILARITY_SEARCH = "similarity_search"
    GRAPH_TRAVERSAL = "graph_traversal"
    RULE_BASED = "rule_based"


@dataclass
class ContextQuery:
    """Schema for context query."""
    query_id: str
    context_type: ContextType
    search_criteria: Dict[str, Any]
    discovery_method: DiscoveryMethod
    target_schema_id: str


@dataclass
class ContextDiscovery:
    """Schema for context discovery."""
    discovery_id: str
    query: ContextQuery
    discovered_contexts: List[Dict[str, Any]]
    discovery_timestamp: str
    confidence_scores: List[float]


@dataclass
class ContextFindingResult:
    """Schema for context finding results."""
    result_id: str
    discovery: ContextDiscovery
    relevant_contexts: List[Dict[str, Any]]
    context_rankings: List[Tuple[str, float]]
    finding_successful: bool