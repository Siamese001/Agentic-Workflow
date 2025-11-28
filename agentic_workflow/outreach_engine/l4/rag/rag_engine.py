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
from l4.high_signal import HighSignalScorer
from l4.temporal_fusion import TemporalRankFusion
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
            
            # Initialize Phase 6 temporal components
            self.high_signal_scorer = HighSignalScorer()
            self.temporal_fusion = TemporalRankFusion()
            
            self._is_stub = False
        except Exception as e:
            # Fallback to stub mode for Phase 4 completion
            logger.warning(f"RAGEngine initialization failed, using stub mode: {e}")
            self.policy = None
            self.pinecone_adapter = None
            self.hybrid_search = None
            self.triplet_store = None
            self.temporal_kg = None
            self.high_signal_scorer = None
            self.temporal_fusion = None
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
        Execute retrieval using underlying components with Phase 6 temporal enhancement.
        
        Args:
            rag_query: RAG query configuration
            
        Returns:
            List of RAG results with temporal and high-signal scoring
        """
        hybrid_scores = []
        kg_scores = []
        temporal_scores = []
        results_text = []
        
        # Hybrid search
        if self.policy.enable_hybrid_search and self.hybrid_search:
            hybrid_config = HybridSearchConfig(
                top_k=rag_query.max_results,
                include_text=True,
                include_metadata=True
            )
            hybrid_results = self.hybrid_search.search(
                query=rag_query.query,
                config=hybrid_config
            )
            # Safety check: ensure hybrid_results is not empty and has required attributes
            if hybrid_results and hasattr(hybrid_results[0], 'fused_score') and hasattr(hybrid_results[0], 'text'):
                hybrid_scores = [r.fused_score for r in hybrid_results]
                results_text = [r.text for r in hybrid_results]
            else:
                logger.warning("Hybrid search returned empty or invalid results")
                hybrid_scores = []
                results_text = []
        
        # Temporal KG search
        if rag_query.include_kg and self.temporal_kg and self.high_signal_scorer:
            try:
                # Search temporal KG with multi-hop traversal
                temporal_metadata = self.temporal_kg.search_temporal(
                    query=rag_query.query,
                    hops=1,  # Default to 1 hop for performance
                    user_id=None
                )
                
                # Compute KG scores based on temporal weights
                kg_scores = [m.weight for m in temporal_metadata]
                
                # Compute high-signal scores for all results
                temporal_scores = []
                for text in results_text:
                    signal_score = self.high_signal_scorer.compute_signal_score(text)
                    temporal_scores.append(signal_score.score)
                
            except Exception as e:
                logger.warning(f"Temporal KG search failed: {e}")
                kg_scores = []
                temporal_scores = []
        
        # Apply TemporalRankFusion if we have temporal components
        if hybrid_scores and self.temporal_fusion and (kg_scores or temporal_scores):
            fused_scores = self.temporal_fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        else:
            # Fallback to hybrid scores only
            fused_scores = hybrid_scores
        
        # Create OutreachRAGResult objects with enriched signal data
        enriched_results = []
        for i, text in enumerate(results_text):
            if i < len(fused_scores):
                # Compute high-signal score for this result
                signal_score = 0.0
                signal_type = None
                if self.high_signal_scorer and text:
                    high_signal = self.high_signal_scorer.compute_signal_score(text)
                    signal_score = high_signal.score
                    signal_type = "high_signal" if signal_score > 0.7 else "moderate_signal"
                
                result = OutreachRAGResult(
                    id=f"rag_{i}",
                    text=text,
                    score=fused_scores[i],
                    company="Unknown",  # Would be extracted from metadata in real implementation
                    title="Search Result",
                    source="rag_engine",
                    signal_score=signal_score,
                    signal_type=signal_type
                )
                enriched_results.append(result)
        
        # Return top N results
        return enriched_results[:rag_query.max_results]
    
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
