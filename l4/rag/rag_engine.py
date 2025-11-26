"""
RAG Engine Facade for LIC Outreach

Thin wrapper over L4 RAG components providing unified retrieval interface.
No heavy logic - pure call-through to underlying components.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from l4.hybrid_search import HybridSearchExecutor, HybridSearchConfig
from l4.pinecone_adapter import PineconeAdapter
from l4.triplet_store import TripletStore, TripletQuery
from l4.temporal_kg import TemporalKG
from l4.schema.outreach_schema import OutreachRAGResult
from l4.rag.lic_rag_policies import get_rag_policy, RAGPolicy


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
        self.policy = get_rag_policy(policy_name)
        
        # Initialize underlying components
        self.hybrid_search = HybridSearchExecutor()
        self.pinecone_adapter = PineconeAdapter()
        self.triplet_store = TripletStore()
        self.temporal_kg = TemporalKG()
    
    def retrieve(self, query: str, profile: Optional[str] = None) -> List[OutreachRAGResult]:
        """
        Unified retrieval method.
        
        Args:
            query: Search query string
            profile: Optional profile name for policy overrides
            
        Returns:
            List of RAG results
        """
        rag_query = RAGQuery(
            query=query,
            profile=profile,
            max_results=self.policy.default_max_results,
            include_kg=self.policy.enable_kg_by_default,
            temporal_window_days=self.policy.default_temporal_window
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
