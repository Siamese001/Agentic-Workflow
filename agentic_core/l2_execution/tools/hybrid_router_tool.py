#!/usr/bin/env python3
"""
Hybrid Router Tool
Section 5: Tool Contracts - Retrieval tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class HybridRouterTool:
    """Hybrid router that chooses between sparse, dense, and hybrid retrieval"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.routing_strategy = self.config.get("routing_strategy", "adaptive")
        self.query_complexity_threshold = self.config.get("query_complexity_threshold", 5)
    
    def route_query(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Route query to optimal retrieval strategy"""
        try:
            strategy = self._determine_strategy(query, documents)
            
            routing_result = {
                "strategy": strategy,
                "query": query,
                "document_count": len(documents),
                "confidence": self._calculate_confidence(query, documents),
                "reasoning": self._get_routing_reasoning(strategy, query)
            }
            
            logger.info(f"Routed query to {strategy} strategy with confidence {routing_result['confidence']:.2f}")
            return routing_result
            
        except Exception as e:
            logger.error(f"Query routing failed: {e}")
            return {"strategy": "sparse", "error": str(e)}
    
    def _determine_strategy(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Determine optimal retrieval strategy"""
        if self.routing_strategy == "always_sparse":
            return "sparse"
        elif self.routing_strategy == "always_dense":
            return "dense"
        elif self.routing_strategy == "always_hybrid":
            return "hybrid"
        else:  # adaptive
            return self._adaptive_routing(query, documents)
    
    def _adaptive_routing(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Adaptive routing based on query and document characteristics"""
        query_length = len(query.split())
        has_embeddings = any(doc.get("embedding") for doc in documents)
        
        # Simple adaptive logic
        if query_length > self.query_complexity_threshold and has_embeddings:
            return "hybrid"
        elif has_embeddings and len(documents) > 100:
            return "dense"
        else:
            return "sparse"
    
    def _calculate_confidence(self, query: str, documents: List[Dict[str, Any]]) -> float:
        """Calculate routing confidence score"""
        query_terms = set(query.lower().split())
        doc_count = len(documents)
        has_embeddings = any(doc.get("embedding") for doc in documents)
        
        # Simple confidence calculation
        confidence = 0.5  # Base confidence
        
        if query_terms:
            confidence += 0.2
        
        if doc_count > 50:
            confidence += 0.2
        
        if has_embeddings:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _get_routing_reasoning(self, strategy: str, query: str) -> str:
        """Get reasoning for routing decision"""
        reasoning_map = {
            "sparse": "Query terms suggest keyword matching will be effective",
            "dense": "Semantic similarity will better capture query intent",
            "hybrid": "Combining keyword and semantic matching for optimal results"
        }
        
        return reasoning_map.get(strategy, "Default routing strategy applied")

def create_hybrid_router_tool(config: Optional[Dict[str, Any]] = None) -> HybridRouterTool:
    """Factory function to create hybrid router tool instance"""
    return HybridRouterTool(config)

# Re-export components
__all__ = [
    'HybridRouterTool', 'create_hybrid_router_tool'
]





