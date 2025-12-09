"""
Vector search execution layer for résumé processing workflows.

Executes vector search operations to support comprehensive résumé enhancement through semantic retrieval.

Layer: L2 (Execution)
Responsibilities:
- Execute vector search operations based on L1 plans for résumé data retrieval
- Transform L4 vector results into L2 execution results for résumé enhancement
- Handle execution errors in résumé processing vector operations

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
    """
    Container for résumé processing vector search results (L2 execution result).

    Provides structured data retrieval results for comprehensive résumé enhancement workflows.
    """
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorSearchExecutor:
    """
    L2 executor for résumé processing vector search operations.
    
    Executes search plans from L1 via L4's PineconeAdapter for résumé enhancement workflows.
    """
    
    def __init__(self, pinecone_adapter: PineconeAdapter):
        """
        Initializes vector search executor for résumé processing workflows.
        
        Args:
            pinecone_adapter: L4 PineconeAdapter instance for résumé data retrieval
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
        Executes vector search operation for résumé processing data retrieval.
        
        Main L2 execution method that takes search plan and executes via L4 for résumé enhancement.
        
        Args:
            namespace: Target namespace for résumé data (from L1 plan)
            query_text: Query text for résumé search (from L1 plan)
            top_k: Number of results for résumé matching (from L1 plan)
            metadata_filter: Optional metadata filters for résumé data (from L1 plan)
            score_threshold: Optional score threshold for résumé relevance (from L1 plan)
            
        Returns:
            List of SearchResult objects for résumé enhancement workflows (L2 execution results)
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
        Executes vector upsert operation for résumé processing data storage.
        
        Args:
            namespace: Target namespace for résumé data storage
            texts: Text content to upsert for résumé enhancement
            record_type: Type of résumé processing records
            metadata_list: Optional metadata for résumé data organization
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



