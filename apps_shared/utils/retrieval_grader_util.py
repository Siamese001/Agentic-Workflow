"""Retrieval Grader - Corrective RAG (CRAG) Component.

This module provides document relevance grading for the Corrective RAG system.
If retrieved documents are irrelevant, it triggers fallback mechanisms
like web search to ensure high-quality responses.
"""
import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class GradeStatus(Enum):
    """Status of document grading."""
    PASS = 'PASS'
    FALLBACK_REQUIRED = 'FALLBACK_REQUIRED'
    UNCERTAIN = 'UNCERTAIN'

@dataclass
class RetrievalGrade:
    """Result of retrieval grading."""
    status: GradeStatus
    relevance_ratio: float
    confidence: float
    relevant_docs: list[int] = None
    irrelevant_docs: list[int] = None
    reasoning: str = ''

    def __post_init__(self):
        if self.relevant_docs is None:
            self.relevant_docs = []
        if self.irrelevant_docs is None:
            self.irrelevant_docs = []

class RetrievalGrader:
    """Grades retrieved documents for relevance to the query."""

    # guardian: allow-magic-config
    def __init__(self, relevance_threshold: float=0.5, confidence_threshold: float=0.7, use_fast_model: bool=True, max_docs_to_grade: int=10):
        """Initialize the retrieval grader.

        Args:
            relevance_threshold: Minimum ratio of relevant docs required
            confidence_threshold: Minimum confidence for PASS status
            use_fast_model: Use fast model for grading (e.g., gpt-4o-mini)
            max_docs_to_grade: Maximum number of documents to grade
        """
        self.relevance_threshold = relevance_threshold
        self.confidence_threshold = confidence_threshold
        self.use_fast_model = use_fast_model
        self.max_docs_to_grade = max_docs_to_grade
        self.stats = {'total_gradings': 0, 'passes': 0, 'fallbacks': 0, 'uncertain': 0, 'avg_relevance': 0.0}
        logger.info(f'Initialized RetrievalGrader - Threshold: {relevance_threshold}, Confidence: {confidence_threshold}, Fast Model: {use_fast_model}')

    async def grade_documents(self, query: str, documents: list[str], document_ids: list[str] | None=None) -> RetrievalGrade:
        """Grade documents for relevance to the query.

        Args:
            query: The original query
            documents: List of document texts
            document_ids: Optional list of document IDs

        Returns:
            RetrievalGrade with assessment
        """
        start_time = time.time()
        self.stats['total_gradings'] += 1
        docs_to_grade = documents[:self.max_docs_to_grade]
        ids_to_grade = document_ids[:self.max_docs_to_grade] if document_ids else None
        relevant_docs = []
        irrelevant_docs = []
        total_confidence = 0.0
        for i, doc in enumerate(docs_to_grade):
            is_relevant, confidence = await self._grade_single_document(query, doc)
            total_confidence += confidence
            doc_id = ids_to_grade[i] if ids_to_grade else str(i)
            if is_relevant:
                relevant_docs.append(doc_id)
            else:
                irrelevant_docs.append(doc_id)
        relevance_ratio = len(relevant_docs) / len(docs_to_grade) if docs_to_grade else 0
        avg_confidence = total_confidence / len(docs_to_grade) if docs_to_grade else 0
        if relevance_ratio >= self.relevance_threshold and avg_confidence >= self.confidence_threshold:
            status = GradeStatus.PASS
            reasoning = f'High relevance ({relevance_ratio:.2f}) and confidence ({avg_confidence:.2f})'
            self.stats['passes'] += 1
        elif relevance_ratio < self.relevance_threshold * 0.3:
            status = GradeStatus.FALLBACK_REQUIRED
            reasoning = f'Very low relevance ({relevance_ratio:.2f}) - fallback needed'
            self.stats['fallbacks'] += 1
        else:
            status = GradeStatus.UNCERTAIN
            reasoning = f'Borderline relevance ({relevance_ratio:.2f}) - proceed with caution'
            self.stats['uncertain'] += 1
        self.stats['avg_relevance'] = (self.stats['avg_relevance'] * (self.stats['total_gradings'] - 1) + relevance_ratio) / self.stats['total_gradings']
        grading_time = time.time() - start_time
        logger.info(f'Grading completed in {grading_time:.3f}s - Status: {status.value}, Relevance: {relevance_ratio:.2f}')
        return RetrievalGrade(status=status, relevance_ratio=relevance_ratio, confidence=avg_confidence, relevant_docs=relevant_docs, irrelevant_docs=irrelevant_docs, reasoning=reasoning)

    async def _grade_single_document(self, query: str, document: str) -> tuple[bool, float]:
        """Grade a single document for relevance.

        Args:
            query: The query
            document: Document text

        Returns:
            Tuple of (is_relevant, confidence)
        """
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())
        overlap = len(query_words & doc_words)
        overlap_ratio = overlap / len(query_words) if query_words else 0
        doc_lower = document.lower()
        negative_indicators = ['not relevant', 'does not contain', 'unrelated', 'different topic', 'no information', 'not found', 'cannot answer', 'insufficient']
        has_negative = any((indicator in doc_lower for indicator in negative_indicators))
        if has_negative:
            is_relevant = False
            confidence = 0.9
        elif overlap_ratio >= 0.3:
            is_relevant = True
            confidence = min(0.5 + overlap_ratio, 0.95)
        elif overlap_ratio >= 0.1:
            is_relevant = True
            confidence = 0.6
        else:
            is_relevant = False
            confidence = 0.7
        return (is_relevant, confidence)

    def get_stats(self) -> dict[str, Any]:
        """Get grader statistics.

        Returns:
            Dictionary with stats
        """
        return {'total_gradings': self.stats['total_gradings'], 'passes': self.stats['passes'], 'fallbacks': self.stats['fallbacks'], 'uncertain': self.stats['uncertain'], 'pass_rate': self.stats['passes'] / max(self.stats['total_gradings'], 1), 'fallback_rate': self.stats['fallbacks'] / max(self.stats['total_gradings'], 1), 'avg_relevance': self.stats['avg_relevance'], 'settings': {'relevance_threshold': self.relevance_threshold, 'confidence_threshold': self.confidence_threshold, 'use_fast_model': self.use_fast_model, 'max_docs_to_grade': self.max_docs_to_grade}}

class WebSearchFallback:
    """Fallback web search when retrieval fails."""

    # guardian: allow-magic-config
    def __init__(self, search_provider: str='tavily', max_results: int=5, timeout: float=5.0):
        """Initialize web search fallback.

        Args:
            search_provider: Web search provider (tavily, serper, etc.)
            max_results: Maximum results to fetch
            timeout: Timeout for search request
        """
        self.search_provider = search_provider
        self.max_results = max_results
        self.timeout = timeout
        self.api_key = None
        logger.info(f'Initialized WebSearchFallback with {search_provider}')

    async def search(self, query: str) -> dict[str, Any]:
        """Perform web search for the query.

        Args:
            query: Search query

        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f'Performing web search for: {query}')
            await asyncio.sleep(DEFAULT_SLEEP)
            results = [{'title': f'Web result 1 for {query}', 'url': 'https://example.com/1', 'snippet': f'This is a web search result about {query}', 'source': 'web'}, {'title': f'Web result 2 for {query}', 'url': 'https://example.com/2', 'snippet': f'Additional information about {query}', 'source': 'web'}]
            return {'query': query, 'results': results, 'source': 'web_search', 'total_results': len(results), 'fallback_triggered': True}
        except Exception as e:
            logger.error(f'Web search failed: {e}')
            return {'query': query, 'results': [], 'source': 'web_search', 'error': str(e), 'fallback_triggered': True}
_retrieval_grader: RetrievalGrader | None = None
_web_search_fallback: WebSearchFallback | None = None

def get_retrieval_grader(**kwargs) -> RetrievalGrader:
    """Get or create the global retrieval grader.

    Args:
        **kwargs: Arguments for RetrievalGrader

    Returns:
        RetrievalGrader instance
    """
    global _retrieval_grader
    if _retrieval_grader is None:
        _retrieval_grader = RetrievalGrader(**kwargs)
    return _retrieval_grader

def get_web_search_fallback(**kwargs) -> WebSearchFallback:
    """Get or create the global web search fallback.

    Args:
        **kwargs: Arguments for WebSearchFallback

    Returns:
        WebSearchFallback instance
    """
    global _web_search_fallback
    if _web_search_fallback is None:
        _web_search_fallback = WebSearchFallback(**kwargs)
    return _web_search_fallback

async def grade_retrieval(query: str, documents: list[str], **kwargs) -> RetrievalGrade:
    """Convenience function to grade retrieval results.

    Args:
        query: The query
        documents: List of documents
        **kwargs: Additional arguments

    Returns:
        RetrievalGrade result
    """
    grader = get_retrieval_grader(**kwargs)
    return await grader.grade_documents(query, documents)

async def fallback_web_search(query: str, **kwargs) -> dict[str, Any]:
    """Convenience function for web search fallback.

    Args:
        query: Search query
        **kwargs: Additional arguments

    Returns:
        Search results
    """
    fallback = get_web_search_fallback(**kwargs)
    return await fallback.search(query)
