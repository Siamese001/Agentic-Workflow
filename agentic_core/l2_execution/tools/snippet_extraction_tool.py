#!/usr/bin/env python3
"""
Snippet Extraction Tool
Section 5: Tool Contracts - Retrieval tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SnippetExtractionTool:
    """Extract best spans from documents for query relevance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_snippet_length = self.config.get("max_snippet_length", 200)
        self.snippet_count = self.config.get("snippet_count", 3)
    
    def extract_snippets(self, query: str, document: str) -> List[Dict[str, Any]]:
        """Extract relevant snippets from document"""
        try:
            # Simple snippet extraction (placeholder implementation)
            sentences = self._split_sentences(document)
            relevant_snippets = []
            
            for sentence in sentences:
                relevance = self._calculate_sentence_relevance(query, sentence)
                if relevance > 0.1:  # Threshold for relevance
                    snippet = self._format_snippet(sentence, relevance)
                    relevant_snippets.append(snippet)
            
            # Sort by relevance and return top snippets
            relevant_snippets.sort(key=lambda x: x["relevance_score"], reverse=True)
            return relevant_snippets[:self.snippet_count]
            
        except Exception as e:
            logger.error(f"Snippet extraction failed: {e}")
            return []
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_sentence_relevance(self, query: str, sentence: str) -> float:
        """Calculate relevance score for sentence"""
        query_terms = set(query.lower().split())
        sentence_terms = set(sentence.lower().split())
        
        if not query_terms:
            return 0.0
        
        overlap = len(query_terms & sentence_terms) / len(query_terms)
        return overlap
    
    def _format_snippet(self, sentence: str, relevance: float) -> Dict[str, Any]:
        """Format snippet with metadata"""
        snippet = sentence[:self.max_snippet_length]
        if len(sentence) > self.max_snippet_length:
            snippet += "..."
        
        return {
            "text": snippet,
            "relevance_score": relevance,
            "length": len(snippet)
        }

def create_snippet_extraction_tool(config: Optional[Dict[str, Any]] = None) -> SnippetExtractionTool:
    """Factory function to create snippet extraction tool instance"""
    return SnippetExtractionTool(config)

# Re-export components
__all__ = [
    'SnippetExtractionTool', 'create_snippet_extraction_tool'
]





