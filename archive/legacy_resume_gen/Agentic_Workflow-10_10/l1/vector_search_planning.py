"""
Vector search planning for résumé evidence retrieval.

Creates structured plans to support comprehensive résumé improvement through semantic search.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class VectorSearchPlan:
    """
    Defines vector search structure for résumé evidence gathering.

    Ensures systematic retrieval of relevant data for comprehensive résumé enhancement.
    """
    query_text: str
    namespace: str
    top_k: int = 5
    metadata_filters: Optional[Dict[str, Any]] = None


@dataclass
class VectorUpsertPlan:
    """
    Structures vector storage planning for résumé data.

    Guides efficient storage of résumé improvement evidence for future retrieval.
    """
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
    """
    Creates vector search plan for résumé evidence retrieval.

    Structures semantic search approach to find relevant data for résumé improvement.
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
    """
    Plans vector storage for résumé improvement data.

    Structures approach to efficiently store résumé evidence for future retrieval.
    """
    if metadata is None:
        metadata = {}
        
    return VectorUpsertPlan(
        id=id,
        text=text,
        namespace=namespace,
        metadata=metadata
    )



