"""L1 Vector search planning layer.

This module contains pure planning functions that generate typed plans for
vector search operations. No actual vector operations are performed here.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class VectorSearchPlan:
    """Plan for executing a vector search operation."""
    query_text: str
    namespace: str
    top_k: int = 5
    metadata_filters: Optional[Dict[str, Any]] = None


@dataclass
class VectorUpsertPlan:
    """Plan for upserting a vector into the store."""
    id: str
    text: str
    namespace: str
    metadata: Dict[str, Any]


def plan_vector_search(
    query: str,
    namespace: str = "default",
    top_k: int = 5,
    metadata_filters: Optional[Dict[str, Any]] = None
) -> VectorSearchPlan:
    """Create a plan for executing a vector search.
    
    Args:
        query: The search query text
        namespace: Namespace to search in (default: "default")
        top_k: Number of results to return (default: 5)
        metadata_filters: Optional filters to apply to the search
        
    Returns:
        VectorSearchPlan containing the search parameters
    """
    return VectorSearchPlan(
        query_text=query,
        namespace=namespace,
        top_k=top_k,
        metadata_filters=metadata_filters or {}
    )


def plan_vector_upsert(
    id: str,
    text: str,
    namespace: str = "default",
    metadata: Optional[Dict[str, Any]] = None
) -> VectorUpsertPlan:
    """Create a plan for upserting a vector.
    
    Args:
        id: Unique identifier for the vector
        text: Text content to embed and store
        namespace: Namespace to store the vector in (default: "default")
        metadata: Additional metadata to store with the vector
        
    Returns:
        VectorUpsertPlan containing the upsert parameters
    """
    if metadata is None:
        metadata = {}
        
    return VectorUpsertPlan(
        id=id,
        text=text,
        namespace=namespace,
        metadata=metadata
    )
