"""
Signal Weighter - Multi-Factor Result Scoring
Ported from legacy_engines/retrieval_enhancements.py

Applies intelligent scoring to retrieval results considering
recency, authority, relevance, and completeness factors.
"""

import logging
import time
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Types of signals for weighting"""
    RECENCY = "recency"
    AUTHORITY = "authority"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONFIDENCE = "confidence"


@dataclass
class SignalWeights:
    """Configurable weights for signal scoring"""
    recency: float = 0.25
    authority: float = 0.25
    relevance: float = 0.35
    completeness: float = 0.15
    
    def normalize(self) -> 'SignalWeights':
        """Normalize weights to sum to 1.0"""
        total = self.recency + self.authority + self.relevance + self.completeness
        if total == 0:
            return SignalWeights()
        return SignalWeights(
            recency=self.recency / total,
            authority=self.authority / total,
            relevance=self.relevance / total,
            completeness=self.completeness / total
        )


@dataclass
class WeightedResult:
    """Result with weighted scoring"""
    content: str
    source: str
    base_score: float
    signal_scores: Dict[str, float]
    final_score: float
    rank: int = 0
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class WeightingResult:
    """Complete result of signal weighting"""
    original_results: List[Dict[str, object]]
    weighted_results: List[WeightedResult]
    weights_used: SignalWeights
    processing_time_ms: int
    top_score: float
    avg_score: float


class SignalWeighter:
    """
    Multi-Factor Result Scoring
    
    Applies intelligent scoring to retrieval results considering
    recency, authority, relevance, and completeness factors.
    """
    
    def __init__(
        self,
        weights: Optional[SignalWeights] = None,
        recency_decay_days: int = 45,
        authority_sources: Optional[Dict[str, float]] = None
    ):
        """
        Initialize signal weighter.
        
        Args:
            weights: Custom signal weights
            recency_decay_days: Days for recency decay calculation
            authority_sources: Source authority mappings
        """
        self.weights = (weights or SignalWeights()).normalize()
        self.recency_decay_days = recency_decay_days
        
        # Default authority scores by source type
        self.authority_sources = authority_sources or {
            "official": 1.0,
            "verified": 0.9,
            "news": 0.8,
            "blog": 0.6,
            "social": 0.5,
            "unknown": 0.4
        }
    
    def weight_results(
        self,
        results: List[Dict[str, object]],
        query: Optional[str] = None,
        context: Optional[Dict[str, object]] = None
    ) -> WeightingResult:
        """
        Apply signal weighting to results.
        
        Args:
            results: Raw results to weight
            query: Original query for relevance calculation
            context: Additional context
            
        Returns:
            WeightingResult with weighted and ranked results
        """
        start_time = time.time()
        context = context or {}
        
        weighted_results = []
        
        for result in results:
            # Calculate individual signal scores
            recency_score = self._calculate_recency_score(result)
            authority_score = self._calculate_authority_score(result)
            relevance_score = self._calculate_relevance_score(result, query)
            completeness_score = self._calculate_completeness_score(result)
            
            signal_scores = {
                SignalType.RECENCY.value: recency_score,
                SignalType.AUTHORITY.value: authority_score,
                SignalType.RELEVANCE.value: relevance_score,
                SignalType.COMPLETENESS.value: completeness_score
            }
            
            # Calculate weighted final score
            final_score = (
                recency_score * self.weights.recency +
                authority_score * self.weights.authority +
                relevance_score * self.weights.relevance +
                completeness_score * self.weights.completeness
            )
            
            # Get foundation score if available
            base_score = result.get('score', result.get('relevance_score', 0.5))
            
            weighted_result = WeightedResult(
                content=result.get('content', ''),
                source=result.get('source', 'unknown'),
                base_score=base_score,
                signal_scores=signal_scores,
                final_score=round(final_score, 4),
                metadata={
                    'original_result': result,
                    'query': query
                }
            )
            
            weighted_results.append(weighted_result)
        
        # Sort by final score and assign ranks
        weighted_results.sort(key=lambda x: x.final_score, reverse=True)
        for i, result in enumerate(weighted_results):
            result.rank = i + 1
        
        # Calculate statistics
        processing_time = int((time.time() - start_time) * 1000)
        top_score = weighted_results[0].final_score if weighted_results else 0.0
        avg_score = sum(r.final_score for r in weighted_results) / len(weighted_results) if weighted_results else 0.0
        
        logger.info(f"Weighted {len(results)} results in {processing_time}ms")
        
        return WeightingResult(
            original_results=results,
            weighted_results=weighted_results,
            weights_used=self.weights,
            processing_time_ms=processing_time,
            top_score=top_score,
            avg_score=round(avg_score, 4)
        )
    
    def _calculate_recency_score(self, result: Dict[str, object]) -> float:
        """Calculate recency score with linear decay."""
        timestamp = result.get('timestamp') or result.get('date') or result.get('published_at')
        
        if not timestamp:
            return 0.5  # Default for unknown recency
        
        try:
            if isinstance(timestamp, str):
                # Parse ISO format
                result_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                result_date = timestamp
            else:
                return 0.5
            
            # Calculate days ago
            now = datetime.now(result_date.tzinfo) if result_date.tzinfo else datetime.now()
            days_ago = (now - result_date).days
            
            if days_ago <= 0:
                return 1.0
            elif days_ago >= self.recency_decay_days:
                return 0.0
            else:
                # Linear decay
                return 1.0 - (days_ago / self.recency_decay_days)
        
        except (ValueError, TypeError) as e:
            logger.debug(f"Error parsing timestamp: {e}")
            return 0.5
    
    def _calculate_authority_score(self, result: Dict[str, object]) -> float:
        """Calculate authority score based on source."""
        # Check for explicit authority score
        if 'authority_score' in result:
            return float(result['authority_score'])
        
        # Determine source type
        source = result.get('source', '').lower()
        source_type = result.get('source_type', 'unknown').lower()
        
        # Check against known authority sources
        for source_key, score in self.authority_sources.items():
            if source_key in source or source_key in source_type:
                return score
        
        return self.authority_sources.get('unknown', 0.4)
    
    def _calculate_relevance_score(self, result: Dict[str, object], query: Optional[str]) -> float:
        """Calculate relevance score."""
        # Check for explicit relevance score
        if 'relevance_score' in result:
            return float(result['relevance_score'])
        
        if not query:
            return 0.5
        
        content = result.get('content', '').lower()
        query_terms = query.lower().split()
        
        if not content or not query_terms:
            return 0.5
        
        # basic term overlap calculation
        matches = sum(1 for term in query_terms if term in content)
        relevance = matches / len(query_terms)
        
        return min(relevance, 1.0)
    
    def _calculate_completeness_score(self, result: Dict[str, object]) -> float:
        """Calculate completeness score based on content richness."""
        content = result.get('content', '')
        
        if not content:
            return 0.0
        
        # Factors for completeness
        word_count = len(content.split())
        has_numbers = any(c.isdigit() for c in content)
        has_proper_nouns = any(word[0].isupper() for word in content.split() if word)
        
        # Calculate score
        length_score = min(word_count / 100, 1.0)  # Normalize to 100 words
        richness_bonus = 0.1 if has_numbers else 0.0
        richness_bonus += 0.1 if has_proper_nouns else 0.0
        
        return min(length_score + richness_bonus, 1.0)
    
    def adjust_weights(
        self,
        recency: Optional[float] = None,
        authority: Optional[float] = None,
        relevance: Optional[float] = None,
        completeness: Optional[float] = None
    ) -> None:
        """Adjust signal weights dynamically."""
        if recency is not None:
            self.weights.recency = recency
        if authority is not None:
            self.weights.authority = authority
        if relevance is not None:
            self.weights.relevance = relevance
        if completeness is not None:
            self.weights.completeness = completeness
        
        self.weights = self.weights.normalize()
        logger.info(f"Adjusted weights: {self.weights}")
    
    def get_top_results(
        self,
        weighting_result: WeightingResult,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[WeightedResult]:
        """Get top K results above minimum score."""
        filtered = [r for r in weighting_result.weighted_results if r.final_score >= min_score]
        return filtered[:top_k]


# builder functions
def create_signal_weighter(
    weights: Optional[SignalWeights] = None,
    recency_decay_days: int = 45
) -> SignalWeighter:
    """Create signal weighter instance."""
    return SignalWeighter(weights, recency_decay_days)


def weight_results(
    results: List[Dict[str, object]],
    query: Optional[str] = None,
    weights: Optional[SignalWeights] = None
) -> WeightingResult:
    """Convenience function to weight results."""
    weighter = SignalWeighter(weights)
    return weighter.weight_results(results, query)


def create_weights(
    recency: float = 0.25,
    authority: float = 0.25,
    relevance: float = 0.35,
    completeness: float = 0.15
) -> SignalWeights:
    """Create signal weights."""
    return SignalWeights(recency, authority, relevance, completeness)
