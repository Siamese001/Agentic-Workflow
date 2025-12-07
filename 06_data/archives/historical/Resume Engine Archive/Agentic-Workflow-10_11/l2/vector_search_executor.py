"""
Vector search execution layer for resume processing workflows.

Executes vector search operations to support comprehensive resume
enhancement through semantic retrieval for job alignment.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from l4 import PineconeAdapter, VectorQueryResult


@dataclass
class SearchResult:
    """
    Container for resume processing vector search results.

    Provides structured data retrieval for resume enhancement
    and job alignment workflows.
    """
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorSearchExecutor:
    """
    L2 executor for resume processing vector search operations.

    Executes search plans from L1 via L4's PineconeAdapter for
    resume enhancement and job alignment workflows.
    """
    
    def __init__(self, pinecone_adapter: PineconeAdapter):
        """
        Initializes vector search executor for resume processing.

        Args:
            pinecone_adapter: L4 PineconeAdapter for resume data retrieval
        """
        self.adapter = pinecone_adapter
    
    def execute_search(
        self,
        namespace: str,
        query_text: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Executes vector search for resume processing data retrieval.

        Main L2 execution method that takes search plan and executes
        via L4 for resume enhancement and job alignment.
        """
        # Delegate to L4 adapter
        l4_results: List[VectorQueryResult] = self.adapter.query_by_text(
            query_text=query_text,
            namespace=namespace,
            top_k=top_k,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
        )
        
        # Transform L4 results to L2 execution results
        return [
            SearchResult(
                id=result.id,
                score=result.score,
                metadata=result.metadata,
            )
            for result in l4_results
        ]
    
    def execute_upsert(
        self,
        namespace: str,
        texts: List[str],
        record_type: str = "doc",
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Executes vector upsert for resume processing data storage.

        Stores resume enhancement data for improved job alignment.
        """
        # Delegate to L4 adapter
        return self.adapter.upsert_text_records(
            texts=texts,
            namespace=namespace,
            record_type=record_type,
            metadata_list=metadata_list,
        )



