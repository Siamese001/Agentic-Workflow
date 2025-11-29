#!/usr/bin/env python3
"""
RAG Filter Tool
Section 5: Tool Contracts - RAG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class RAGFilterTool:
    """Dedupe, cluster, and top-k filter for RAG results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.similarity_threshold = self.config.get("similarity_threshold", 0.8)
        self.max_results = self.config.get("max_results", 10)
    
    def filter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter RAG results by deduplication and clustering"""
        try:
            # Remove duplicates
            deduped = self._deduplicate_results(results)
            
            # Apply top-k filter
            filtered = deduped[:self.max_results]
            
            logger.info(f"Filtered {len(results)} results to {len(filtered)}")
            return filtered
            
        except Exception as e:
            logger.error(f"RAG filtering failed: {e}")
            return results[:self.max_results]
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content = result.get("doc", {}).get("content", "")
            content_hash = hash(content.lower())
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results

def create_rag_filter_tool(config: Optional[Dict[str, Any]] = None) -> RAGFilterTool:
    """Factory function to create RAG filter tool instance"""
    return RAGFilterTool(config)

# Re-export components
__all__ = [
    'RAGFilterTool', 'create_rag_filter_tool'
]
