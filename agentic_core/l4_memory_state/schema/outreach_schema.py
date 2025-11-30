# outreach_schema - Schema definitions for outreach RAG results
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Search result from hybrid search"""
    content: str
    confidence: float
    metadata: Dict[str, Any]
    temporal_score: float = 0.0
    
    def __post_init__(self):
        if not isinstance(self.metadata, dict):
            self.metadata = {}

@dataclass
class OutreachRAGResult:
    """RAG result formatted for outreach operations"""
    content: str
    confidence: float
    metadata: Dict[str, Any]
    temporal_score: float = 0.0
    outreach_relevance: float = 0.0
    
    def __post_init__(self):
        if not isinstance(self.metadata, dict):
            self.metadata = {}

def format_as_outreach_result(search_result: SearchResult) -> OutreachRAGResult:
    """Convert SearchResult to OutreachRAGResult"""
    return OutreachRAGResult(
        content=search_result.content,
        confidence=search_result.confidence,
        metadata=search_result.metadata,
        temporal_score=search_result.temporal_score,
        outreach_relevance=0.8
    )
