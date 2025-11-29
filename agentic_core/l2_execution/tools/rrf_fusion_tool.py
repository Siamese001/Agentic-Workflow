#!/usr/bin/env python3
"""
RRF Fusion Tool
Section 5: Tool Contracts - RAG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class RRFFusionTool:
    """Reciprocal Rank Fusion for combining multiple retrieval results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.k = self.config.get("k", 60)  # RRF constant
        self.top_k = self.config.get("top_k", 10)
    
    def fuse_results(self, result_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Fuse multiple result lists using RRF"""
        try:
            if not result_lists:
                return []
            
            # Calculate RRF scores
            doc_scores = {}
            
            for result_list in result_lists:
                for rank, result in enumerate(result_list, 1):
                    doc_id = self._get_doc_id(result)
                    rrf_score = 1.0 / (self.k + rank)
                    
                    if doc_id in doc_scores:
                        doc_scores[doc_id]["rrf_score"] += rrf_score
                        doc_scores[doc_id]["sources"].append(result)
                    else:
                        doc_scores[doc_id] = {
                            "rrf_score": rrf_score,
                            "doc": result.get("doc", result),
                            "sources": [result]
                        }
            
            # Sort by RRF score and return top_k
            fused_results = sorted(doc_scores.values(), key=lambda x: x["rrf_score"], reverse=True)
            return fused_results[:self.top_k]
            
        except Exception as e:
            logger.error(f"RRF fusion failed: {e}")
            return []
    
    def _get_doc_id(self, result: Dict[str, Any]) -> str:
        """Get document ID from result"""
        doc = result.get("doc", {})
        return doc.get("id", str(hash(str(doc))))

def create_rrf_fusion_tool(config: Optional[Dict[str, Any]] = None) -> RRFFusionTool:
    """Factory function to create RRF fusion tool instance"""
    return RRFFusionTool(config)

# Re-export components
__all__ = [
    'RRFFusionTool', 'create_rrf_fusion_tool'
]





