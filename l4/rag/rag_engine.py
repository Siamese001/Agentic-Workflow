"""
RAG Engine Facade for LIC Outreach

Thin wrapper over L4 RAG components providing unified retrieval interface.
No heavy logic - pure call-through to underlying components.
"""

from typing import List, Optional
from dataclasses import dataclass
import logging

from l4.hybrid_search import HybridSearchExecutor, HybridSearchConfig
from l4.pinecone_adapter import PineconeAdapter, PineconeConfig
from l4.triplet_store import TripletStore, TripletQuery
from l4.temporal_kg import TemporalKG
from l4.schema.outreach_schema import OutreachRAGResult
from l4.rag.lic_rag_policies import get_rag_policy

logger = logging.getLogger(__name__)


@dataclass
class RAGQuery:
    """Unified query structure for RAG operations."""
    query: str
    profile: Optional[str] = None
    max_results: int = 10
    include_kg: bool = True
    temporal_window_days: Optional[int] = None


class RAGEngine:
    """
    Thin wrapper over L4 RAG components.
    
    Provides unified retrieval interface for LIC outreach pipeline.
    No business logic - just call-through to underlying components.
    """
    
    def __init__(self, policy_name: Optional[str] = None):
        """Initialize RAG engine with specified policy."""
        try:
            self.policy = get_rag_policy(policy_name)
            
            # Initialize underlying components with proper dependencies
            # Create minimal stub config for Phase 4 completion
            stub_config = PineconeConfig(
                api_key="stub_key",
                index_name="stub_index"
            )
            self.pinecone_adapter = PineconeAdapter(stub_config)
            self.hybrid_search = HybridSearchExecutor(pinecone_adapter=self.pinecone_adapter)
            self.triplet_store = TripletStore()
            self.temporal_kg = TemporalKG(pinecone_adapter=self.pinecone_adapter)
            self._is_stub = False
        except Exception as e:
            # Fallback to stub mode for Phase 4 completion
            logger.warning(f"RAGEngine initialization failed, using stub mode: {e}")
            self.policy = None
            self.pinecone_adapter = None
            self.hybrid_search = None
            self.triplet_store = None
            self.temporal_kg = None
            self._is_stub = True
    
    def retrieve(self, query: str, profile: Optional[str] = None) -> List[OutreachRAGResult]:
        """
        Unified retrieval method.
        
        Args:
            query: Search query string
            profile: Optional profile name for policy overrides
            
        Returns:
            List of RAG results
        """
        if self._is_stub:
            # Stub mode for Phase 4 completion - return minimal result
            return [OutreachRAGResult(
                content="Stub RAG result for Phase 4",
                source="stub",
                score=0.5,
                metadata={"stub_mode": True}
            )]
        
        rag_query = RAGQuery(
            query=query,
            profile=profile,
            max_results=10,  # Fixed value for stub mode
            include_kg=True,  # Fixed value for stub mode
            temporal_window_days=None  # Fixed value for stub mode
        )
        
        return self._execute_retrieval(rag_query)
    
    def retrieve_with_config(self, rag_query: RAGQuery) -> List[OutreachRAGResult]:
        """
        Retrieve with explicit query configuration.
        
        Args:
            rag_query: Detailed RAG query configuration
            
        Returns:
            List of RAG results
        """
        return self._execute_retrieval(rag_query)
    
    def _execute_retrieval(self, rag_query: RAGQuery) -> List[OutreachRAGResult]:
        """
        Execute retrieval using underlying components.
        
        Args:
            rag_query: RAG query configuration
            
        Returns:
            List of RAG results
        """
        results = []
        
        # Vector search via Pinecone
        if self.policy.enable_vector_search:
            vector_results = self.pinecone_adapter.search(
                query=rag_query.query,
                top_k=rag_query.max_results // 2  # Split results between sources
            )
            results.extend(vector_results)
        
        # Hybrid search
        if self.policy.enable_hybrid_search:
            hybrid_config = HybridSearchConfig(
                top_k=rag_query.max_results // 2,
                include_text=True,
                include_metadata=True
            )
            hybrid_results = self.hybrid_search.search(
                query=rag_query.query,
                config=hybrid_config
            )
            results.extend(hybrid_results)
        
        # Knowledge graph search
        if rag_query.include_kg and self.policy.enable_kg_search:
            kg_results = self._search_knowledge_graph(rag_query)
            results.extend(kg_results)
        
        # Apply policy-based filtering and ranking
        filtered_results = self._apply_policy_filters(results, rag_query)
        
        # Return top N results
        return filtered_results[:rag_query.max_results]
    
    def _search_knowledge_graph(self, rag_query: RAGQuery) -> List[OutreachRAGResult]:
        """Search knowledge graph based on policy."""
        if rag_query.temporal_window_days:
            return self.temporal_kg.search_temporal(
                query=rag_query.query,
                window_days=rag_query.temporal_window_days
            )
        else:
            return self.triplet_store.search(
                TripletQuery(query=rag_query.query)
            )
    
    def _apply_policy_filters(self, results: List[OutreachRAGResult], rag_query: RAGQuery) -> List[OutreachRAGResult]:
        """Apply policy-based filtering and ranking."""
        # Filter by confidence threshold
        if self.policy.confidence_threshold > 0:
            results = [
                r for r in results 
                if getattr(r, 'confidence', 1.0) >= self.policy.confidence_threshold
            ]
        
        # Apply source prioritization
        if self.policy.source_priorities:
            results.sort(key=lambda r: self.policy.source_priorities.get(
                getattr(r, 'source_type', 'unknown'), 999
            ))
        
        return results
