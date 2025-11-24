"""L2 Vector search execution layer.

REFACTORED: Now uses L4 PineconeAdapter instead of direct Pinecone access.
This enforces proper layer boundaries (L2 execution should not directly
access external services - that's L4's responsibility).

Layer: L2 (Execution)
Responsibilities:
- Execute vector search operations based on L1 plans
- Transform L4 vector results into L2 execution results
- Handle execution errors

Non-responsibilities:
- Planning queries (L1)
- Managing vector store state (L4)
- Orchestration (L3)
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from l4 import PineconeAdapter, VectorQueryResult


@dataclass
class SearchResult:
    """Container for vector search results (L2 execution result)."""
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorSearchExecutor:
    """L2 executor for vector search operations.
    
    This executor receives search plans from L1 and executes them via L4's
    PineconeAdapter. It does NOT directly access Pinecone or manage state.
    """
    
    def __init__(self, pinecone_adapter: PineconeAdapter):
        """Initialize with L4 Pinecone adapter.
        
        Args:
            pinecone_adapter: L4 PineconeAdapter instance
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
        """Execute a vector search operation.
        
        This is the main L2 execution method that takes a search plan
        and executes it via L4.
        
        Args:
            namespace: Target namespace (from L1 plan)
            query_text: Query text (from L1 plan)
            top_k: Number of results (from L1 plan)
            metadata_filter: Optional metadata filters (from L1 plan)
            score_threshold: Optional score threshold (from L1 plan)
            
        Returns:
            List of SearchResult objects (L2 execution results)
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
        """Execute a vector upsert operation.
        
        Args:
            namespace: Target namespace
            texts: Text content to upsert
            record_type: Type prefix for IDs
            metadata_list: Optional metadata for each text
            
        Returns:
            List of generated record IDs
        """
        # Delegate to L4 adapter
        return self.adapter.upsert_text_records(
            texts=texts,
            namespace=namespace,
            record_type=record_type,
            metadata_list=metadata_list,
        )
