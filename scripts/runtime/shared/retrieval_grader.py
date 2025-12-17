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
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class GradeStatus(Enum):
    """Status of document grading."""
    PASS = "pass"
    FALLBACK_REQUIRED = "FALLBACK_REQUIRED"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class RetrievalGrade:
    """Result of retrieval grading."""
    status: GradeStatus
    relevance_ratio: float
    confidence: float
    relevant_docs: List[int] = None
    irrelevant_docs: List[int] = None
    REASONING: str = ""

    def __post_init__(self):
        if self.relevant_docs is None:
            self.relevant_docs = []
        if self.irrelevant_docs is None:
            self.irrelevant_docs = []


class RetrievalGrader:
    """Grades retrieved documents for relevance to the query."""

    def __init__(self,
                 relevance_threshold: float = 0.5,
                 confidence_threshold: float = 0.7,
                 use_fast_model: bool = True,
                 max_docs_to_grade: int = 10):
        """Initialize the retrieval grader.

        Args:
            relevance_threshold: Minimum ratio of relevant docs required
            confidence_threshold: Minimum confidence for pass status
            use_fast_model: Use fast model for grading (e.g., gpt-4o-mini)
            max_docs_to_grade: Maximum number of documents to grade
        """
        self.relevance_threshold = relevance_threshold
        self.confidence_threshold = confidence_threshold
        self.use_fast_model = use_fast_model
        self.max_docs_to_grade = max_docs_to_grade

        # Statistics
        self.STATS = {
            "total_gradings": 0,
            "passes": 0,
            "fallbacks": 0,
            "uncertain": 0,
            "avg_relevance": 0.0
        }

        LOGGER.info(f"Initialized RetrievalGrader - Threshold: {relevance_threshold}, "
                   f"Confidence: {confidence_threshold}, Fast Model: {use_fast_model}")

        """Docstring."""
    async def grade_documents(self,
                            query: str,
                            documents: List[str],
                            document_ids: Optional[List[str]] = None) -> RetrievalGrade:
            """Grade documents for relevance to the query.

        Args:
            query: The original query
            documents: List of document texts
            document_ids: Optional list of document IDs

        Returns:
            RetrievalGrade with assessment
        """
            start_time = time.time()
            self.STATS["total_gradings"] += 1

            # Limit documents to grade
            docs_to_grade = documents[:self.max_docs_to_grade]
            ids_to_grade = document_ids[:self.max_docs_to_grade] if document_ids else None

            # Grade each document
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

            # Calculate overall metrics
            relevance_ratio = len(relevant_docs) / len(docs_to_grade) if docs_to_grade else 0
            avg_confidence = total_confidence / len(docs_to_grade) if docs_to_grade else 0

            # Determine status
            if relevance_ratio >= self.relevance_threshold and avg_confidence >= self.confidence_threshold:
                status = GradeStatus.PASS
                REASONING = f"High relevance ({relevance_ratio:.2f}) and confidence ({avg_confidence:.2f})"
                self.STATS["passes"] += 1
            elif relevance_ratio < self.relevance_threshold * 0.3:
                status = GradeStatus.FALLBACK_REQUIRED
                REASONING = f"Very low relevance ({relevance_ratio:.2f}) - fallback needed"
                self.STATS["fallbacks"] += 1
            else:
                status = GradeStatus.UNCERTAIN
                REASONING = f"Borderline relevance ({relevance_ratio:.2f}) - proceed with caution"
                self.STATS["uncertain"] += 1

            # Update stats
            self.STATS["avg_relevance"] = (
                (self.STATS["avg_relevance"] * (self.STATS["total_gradings"] - 1) + relevance_ratio)
                / self.STATS["total_gradings"]
            )

            grading_time = time.time() - start_time
            LOGGER.info(f"Grading completed in {grading_time:.3f}s - "
                       f"Status: {status.value}, Relevance: {relevance_ratio:.2f}")

            return RetrievalGrade(
                status=status,
                relevance_ratio=relevance_ratio,
                confidence=avg_confidence,
                relevant_docs=relevant_docs,
                irrelevant_docs=irrelevant_docs,
                REASONING=REASONING
            )

    async def _grade_single_document(self, query: str, document: str) -> Tuple[bool, float]:
            """Grade a single document for relevance.

        Args:
            query: The query
            document: Document text

        Returns:
            Tuple of (is_relevant, confidence)
        """
            # For fast grading, use keyword and semantic analysis
            # In production, this could use an LLM call

            # Extract keywords from query
            query_words = set(query.lower().split())
            doc_words = set(document.lower().split())

            # Calculate overlap
            overlap = len(query_words & doc_words)
            overlap_ratio = overlap / len(query_words) if query_words else 0

            # Check for explicit negation or irrelevance
            doc_lower = document.lower()
            negative_indicators = [
                "not relevant", "does not contain", "unrelated", "different topic",
                "no information", "not found", "cannot answer", "insufficient"
            ]

            has_negative = any(indicator in doc_lower for indicator in negative_indicators)

            # Determine relevance
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

            return is_relevant, confidence

    def get_stats(self) -> Dict[str, Any]:
            """Get grader statistics.

        Returns:
            Dictionary with stats
        """
            return {
                "total_gradings": self.STATS["total_gradings"],
                "passes": self.STATS["passes"],
                "fallbacks": self.STATS["fallbacks"],
                "uncertain": self.STATS["uncertain"],
                "pass_rate": self.STATS["passes"] / max(self.STATS["total_gradings"], 1),
                "fallback_rate": self.STATS["fallbacks"] / max(self.STATS["total_gradings"], 1),
                "avg_relevance": self.STATS["avg_relevance"],
                "settings": {
                    "relevance_threshold": self.relevance_threshold,
                    "confidence_threshold": self.confidence_threshold,
                    "use_fast_model": self.use_fast_model,
                    "max_docs_to_grade": self.max_docs_to_grade
                }
            }

class WebSearchFallback:
    """Fallback web search when retrieval fails."""

    def __init__(self,
                 search_provider: str = "tavily",
                 max_results: int = 5,
                 timeout: float = 5.0):
            """Initialize web search fallback.

        Args:
            search_provider: Web search provider (tavily, serper, etc.)
            max_results: Maximum results to fetch
            timeout: Timeout for search request
        """
            self.search_provider = search_provider
            self.max_results = max_results
            self.TIMEOUT = timeout
            self.api_key = None  # In production, load from config

            LOGGER.info(f"Initialized WebSearchFallback with {search_provider}")

    async def search(self, query: str) -> Dict[str, Any]:
            """Perform web search for the query.

        Args:
            query: Search query

        Returns:
            Dictionary with search results
        """
            try:
                # Mock implementation - in production, call actual search API
                LOGGER.info(f"Performing web search for: {query}")

                # Simulate API call
                await asyncio.sleep(0.5)

                # Mock results
                results = [
                    {
                        "title": f"Web result 1 for {query}",
                        "url": "https://example.com/1",
                        "snippet": f"This is a web search result about {query}",
                        "source": "web"
                    },
                    {
                        "title": f"Web result 2 for {query}",
                        "url": "https://example.com/2",
                        "snippet": f"Additional information about {query}",
                        "source": "web"
                    }
                ]

                return {
                    "query": query,
                    "results": results,
                    "source": "web_search",
                    "total_results": len(results),
                    "fallback_triggered": True
                }

            except Exception as e:
LOGGER.error(f"Web search failed: {e}")
                return {
                    "query": query,
                    "results": [],
                    "source": "web_search",
                    "error": str(e),
                    "fallback_triggered": True
                }

# Global instances
_retrieval_grader: Optional[RetrievalGrader] = None
_web_search_fallback: Optional[WebSearchFallback] = None

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

# Convenience functions
async def grade_retrieval(query: str, documents: List[str], **kwargs) -> RetrievalGrade:
    """Convenience function to grade retrieval results.

    Args:
        query: The query
        documents: List of documents
        **kwargs: Additional arguments

    Returns:
        RetrievalGrade result
    """
    GRADER = get_retrieval_grader(**kwargs)
    return await GRADER.grade_documents(query, documents)

async def fallback_web_search(query: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for web search fallback.

    Args:
        query: Search query
        **kwargs: Additional arguments

    Returns:
        Search results
    """
    FALLBACK = get_web_search_fallback(**kwargs)
    return await FALLBACK.search(query)

