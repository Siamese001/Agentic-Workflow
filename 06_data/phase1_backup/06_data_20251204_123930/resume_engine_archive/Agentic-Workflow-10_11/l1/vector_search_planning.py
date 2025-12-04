"""
Vector search planning for resume evidence retrieval and semantic matching.

Creates structured plans to support comprehensive resume improvement
through semantic search and job alignment.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class VectorSearchPlan:
    """
    Defines vector search structure for resume evidence gathering.

    Ensures systematic retrieval of relevant data for comprehensive
    resume enhancement and job alignment.
    """
    query_text: str
    namespace: str
    top_k: int = 5
    metadata_filters: Optional[Dict[str, Any]] = None


@dataclass
class VectorUpsertPlan:
    """
    Structures vector storage planning for resume data.

    Guides efficient storage of resume improvement evidence
    for future retrieval and job alignment.
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
    Creates vector search plan for resume evidence retrieval.

    Structures semantic search approach to find relevant data
    for resume improvement and job alignment.
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
    Plans vector storage for resume improvement data.

    Structures approach to efficiently store resume evidence
    for future retrieval and job alignment.
    """
    if metadata is None:
        metadata = {}
        
    return VectorUpsertPlan(
        id=id,
        text=text,
        namespace=namespace,
        metadata=metadata
    )



