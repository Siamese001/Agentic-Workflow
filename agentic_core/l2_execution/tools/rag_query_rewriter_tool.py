#!/usr/bin/env python3
"""
RAG Query Rewriter Tool
Section 5: Tool Contracts - RAG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class RAGQueryRewriterTool:
    """Query rewrite and expansion for RAG systems"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.expansion_terms = self.config.get("expansion_terms", 3)
        self.rewrite_strategy = self.config.get("rewrite_strategy", "synonym_expansion")
    
    def rewrite_query(self, query: str) -> Dict[str, Any]:
        """Rewrite and expand query for better retrieval"""
        try:
            expanded_terms = self._generate_expansion_terms(query)
            rewritten_query = self._construct_expanded_query(query, expanded_terms)
            
            result = {
                "original_query": query,
                "rewritten_query": rewritten_query,
                "expansion_terms": expanded_terms,
                "strategy": self.rewrite_strategy
            }
            
            logger.info(f"Query rewritten: {query} -> {rewritten_query}")
            return result
            
        except Exception as e:
            logger.error(f"Query rewriting failed: {e}")
            return {"original_query": query, "rewritten_query": query, "error": str(e)}
    
    def _generate_expansion_terms(self, query: str) -> List[str]:
        """Generate expansion terms for query"""
        # Simple expansion logic (placeholder)
        term_expansions = {
            "python": ["programming", "coding", "software"],
            "developer": ["engineer", "programmer", "software"],
            "aws": ["amazon", "cloud", "infrastructure"],
            "machine": ["ml", "artificial", "ai"],
            "learning": ["training", "education", "study"]
        }
        
        expanded_terms = []
        query_terms = query.lower().split()
        
        for term in query_terms:
            if term in term_expansions:
                expanded_terms.extend(term_expansions[term][:self.expansion_terms])
        
        return expanded_terms[:self.expansion_terms]
    
    def _construct_expanded_query(self, original: str, expansions: List[str]) -> str:
        """Construct expanded query"""
        if expansions:
            return f"{original} {' '.join(expansions)}"
        return original

def create_rag_query_rewriter_tool(config: Optional[Dict[str, Any]] = None) -> RAGQueryRewriterTool:
    """Factory function to create RAG query rewriter tool instance"""
    return RAGQueryRewriterTool(config)

# Re-export components
__all__ = [
    'RAGQueryRewriterTool', 'create_rag_query_rewriter_tool'
]
