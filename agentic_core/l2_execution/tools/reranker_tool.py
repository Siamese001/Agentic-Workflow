#!/usr/bin/env python3
"""
Reranker Tool
Section 5: Tool Contracts - Retrieval tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class RerankerTool:
    """Cross-encoder re-ranker for improving retrieval results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_name = self.config.get("model_name", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.top_k = self.config.get("top_k", 10)
        self.batch_size = self.config.get("batch_size", 32)
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance"""
        try:
            if not documents:
                return []
            
            # Calculate relevance scores
            scored_docs = []
            for doc in documents:
                relevance_score = self._calculate_relevance(query, doc)
                scored_docs.append({
                    "doc": doc,
                    "relevance_score": relevance_score,
                    "original_score": doc.get("score", 0.0)
                })
            
            # Sort by relevance score
            scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Return top_k results
            k = top_k or self.top_k
            return scored_docs[:k]
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return []
    
    def _calculate_relevance(self, query: str, document: Dict[str, Any]) -> float:
        """Calculate relevance score for query-document pair"""
        content = document.get("content", "")
        title = document.get("title", "")
        
        # Simple relevance calculation (placeholder for cross-encoder)
        query_terms = set(query.lower().split())
        content_terms = set(content.lower().split())
        title_terms = set(title.lower().split())
        
        # Term overlap scoring
        content_overlap = len(query_terms & content_terms) / len(query_terms) if query_terms else 0
        title_overlap = len(query_terms & title_terms) / len(query_terms) if query_terms else 0
        
        # Weighted combination
        relevance = 0.7 * content_overlap + 0.3 * title_overlap
        
        # Boost for exact matches
        if query.lower() in content.lower():
            relevance += 0.2
        
        return min(1.0, relevance)
    
    def batch_rerank(self, queries: List[str], documents_list: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """Batch rerank multiple queries"""
        try:
            results = []
            for query, documents in zip(queries, documents_list):
                reranked = self.rerank(query, documents)
                results.append(reranked)
            
            logger.info(f"Batch reranked {len(queries)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Batch reranking failed: {e}")
            return [[] for _ in queries]

def create_reranker_tool(config: Optional[Dict[str, Any]] = None) -> RerankerTool:
    """Factory function to create reranker tool instance"""
    return RerankerTool(config)

# Re-export components
__all__ = [
    'RerankerTool', 'create_reranker_tool'
]





