"""
Evidence Ranker - Quality-Based Evidence Scoring
Ported from legacy_engines/content_quality_enhancements.py

Scores and ranks evidence based on relevance, authority,
freshness, and completeness for improved evidence utilization.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of evidence"""
    FACT = "fact"
    STATISTIC = "statistic"
    QUOTE = "quote"
    EXAMPLE = "example"
    REFERENCE = "reference"
    CLAIM = "claim"


class EvidenceQuality(Enum):
    """Quality levels for evidence"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class EvidenceItem:
    """Individual evidence item with scoring"""
    evidence_id: str
    content: str
    source: str
    evidence_type: EvidenceType
    relevance_score: float
    authority_score: float
    freshness_score: float
    completeness_score: float
    quality_score: float
    final_rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingResult:
    """Result of evidence ranking"""
    query: str
    ranked_evidence: List[EvidenceItem]
    top_evidence: List[EvidenceItem]
    quality_distribution: Dict[str, int]
    processing_time_ms: int
    avg_quality_score: float


class EvidenceRanker:
    """
    Quality-Based Evidence Scoring and Ranking
    
    Scores and ranks evidence based on relevance, authority,
    freshness, and completeness for improved evidence utilization.
    """
    
    def __init__(
        self,
        relevance_weight: float = 0.35,
        authority_weight: float = 0.25,
        freshness_weight: float = 0.20,
        completeness_weight: float = 0.20,
        freshness_decay_days: int = 90
    ):
        """
        Initialize evidence ranker.
        
        Args:
            relevance_weight: Weight for relevance scoring
            authority_weight: Weight for authority scoring
            freshness_weight: Weight for freshness scoring
            completeness_weight: Weight for completeness scoring
            freshness_decay_days: Days for freshness decay
        """
        self.relevance_weight = relevance_weight
        self.authority_weight = authority_weight
        self.freshness_weight = freshness_weight
        self.completeness_weight = completeness_weight
        self.freshness_decay_days = freshness_decay_days
        
        # Normalize weights
        total = relevance_weight + authority_weight + freshness_weight + completeness_weight
        if total > 0:
            self.relevance_weight /= total
            self.authority_weight /= total
            self.freshness_weight /= total
            self.completeness_weight /= total
        
        # Authority source mappings
        self.authority_sources = {
            "official": 1.0,
            "academic": 0.95,
            "verified": 0.9,
            "news": 0.8,
            "industry": 0.75,
            "blog": 0.5,
            "social": 0.4,
            "unknown": 0.3
        }
    
    def rank_evidence(
        self,
        evidence_items: List[Dict[str, Any]],
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> RankingResult:
        """
        Rank evidence items by quality.
        
        Args:
            evidence_items: Raw evidence items to rank
            query: Query for relevance calculation
            context: Additional context
            top_k: Number of top items to highlight
            
        Returns:
            RankingResult with ranked evidence
        """
        start_time = time.time()
        context = context or {}
        
        ranked_items = []
        
        for i, item in enumerate(evidence_items):
            evidence_id = item.get('id', f"evidence_{i}")
            content = item.get('content', '')
            source = item.get('source', 'unknown')
            
            # Calculate individual scores
            relevance_score = self._calculate_relevance(content, query)
            authority_score = self._calculate_authority(item)
            freshness_score = self._calculate_freshness(item)
            completeness_score = self._calculate_completeness(content)
            
            # Calculate weighted quality score
            quality_score = (
                relevance_score * self.relevance_weight +
                authority_score * self.authority_weight +
                freshness_score * self.freshness_weight +
                completeness_score * self.completeness_weight
            )
            
            # Determine evidence type
            evidence_type = self._determine_evidence_type(content)
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                content=content,
                source=source,
                evidence_type=evidence_type,
                relevance_score=round(relevance_score, 4),
                authority_score=round(authority_score, 4),
                freshness_score=round(freshness_score, 4),
                completeness_score=round(completeness_score, 4),
                quality_score=round(quality_score, 4),
                metadata=item.get('metadata', {})
            )
            
            ranked_items.append(evidence_item)
        
        # Sort by quality score and assign ranks
        ranked_items.sort(key=lambda x: x.quality_score, reverse=True)
        for i, item in enumerate(ranked_items):
            item.final_rank = i + 1
        
        # Get top evidence
        top_evidence = ranked_items[:top_k]
        
        # Calculate quality distribution
        quality_distribution = self._calculate_quality_distribution(ranked_items)
        
        # Calculate average quality
        avg_quality = sum(e.quality_score for e in ranked_items) / len(ranked_items) if ranked_items else 0.0
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Ranked {len(ranked_items)} evidence items in {processing_time}ms")
        
        return RankingResult(
            query=query,
            ranked_evidence=ranked_items,
            top_evidence=top_evidence,
            quality_distribution=quality_distribution,
            processing_time_ms=processing_time,
            avg_quality_score=round(avg_quality, 4)
        )
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score based on query matching."""
        if not content or not query:
            return 0.0
        
        content_lower = content.lower()
        query_terms = query.lower().split()
        
        if not query_terms:
            return 0.5
        
        # Count matching terms
        matches = sum(1 for term in query_terms if term in content_lower)
        base_relevance = matches / len(query_terms)
        
        # Boost for exact phrase match
        if query.lower() in content_lower:
            base_relevance = min(base_relevance + 0.2, 1.0)
        
        return base_relevance
    
    def _calculate_authority(self, item: Dict[str, Any]) -> float:
        """Calculate authority score based on source."""
        # Check for explicit authority score
        if 'authority_score' in item:
            return float(item['authority_score'])
        
        source = item.get('source', '').lower()
        source_type = item.get('source_type', 'unknown').lower()
        
        # Check against known authority sources
        for source_key, score in self.authority_sources.items():
            if source_key in source or source_key in source_type:
                return score
        
        return self.authority_sources.get('unknown', 0.3)
    
    def _calculate_freshness(self, item: Dict[str, Any]) -> float:
        """Calculate freshness score based on date."""
        # Check for explicit freshness score
        if 'freshness_score' in item:
            return float(item['freshness_score'])
        
        timestamp = item.get('timestamp') or item.get('date') or item.get('published_at')
        
        if not timestamp:
            return 0.5  # Default for unknown freshness
        
        try:
            if isinstance(timestamp, str):
                item_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                item_date = timestamp
            else:
                return 0.5
            
            now = datetime.now(item_date.tzinfo) if item_date.tzinfo else datetime.now()
            days_ago = (now - item_date).days
            
            if days_ago <= 0:
                return 1.0
            elif days_ago >= self.freshness_decay_days:
                return 0.1
            else:
                return 1.0 - (days_ago / self.freshness_decay_days) * 0.9
        
        except (ValueError, TypeError):
            return 0.5
    
    def _calculate_completeness(self, content: str) -> float:
        """Calculate completeness score based on content richness."""
        if not content:
            return 0.0
        
        # Factors for completeness
        word_count = len(content.split())
        has_numbers = any(c.isdigit() for c in content)
        has_proper_structure = '.' in content or ',' in content
        
        # Length score (optimal around 50-200 words)
        if word_count < 10:
            length_score = 0.2
        elif word_count < 50:
            length_score = 0.5 + (word_count - 10) / 80
        elif word_count <= 200:
            length_score = 1.0
        else:
            length_score = max(0.7, 1.0 - (word_count - 200) / 500)
        
        # Richness bonus
        richness_bonus = 0.0
        if has_numbers:
            richness_bonus += 0.1
        if has_proper_structure:
            richness_bonus += 0.1
        
        return min(length_score + richness_bonus, 1.0)
    
    def _determine_evidence_type(self, content: str) -> EvidenceType:
        """Determine the type of evidence based on content."""
        content_lower = content.lower()
        
        # Check for statistics
        if any(c.isdigit() for c in content) and ('%' in content or 'percent' in content_lower):
            return EvidenceType.STATISTIC
        
        # Check for quotes
        if '"' in content or "'" in content or 'said' in content_lower or 'according to' in content_lower:
            return EvidenceType.QUOTE
        
        # Check for examples
        if 'example' in content_lower or 'for instance' in content_lower or 'such as' in content_lower:
            return EvidenceType.EXAMPLE
        
        # Check for references
        if 'http' in content_lower or 'www.' in content_lower or 'source:' in content_lower:
            return EvidenceType.REFERENCE
        
        # Check for claims
        if 'claim' in content_lower or 'assert' in content_lower or 'believe' in content_lower:
            return EvidenceType.CLAIM
        
        return EvidenceType.FACT
    
    def _calculate_quality_distribution(self, items: List[EvidenceItem]) -> Dict[str, int]:
        """Calculate distribution of quality levels."""
        distribution = {
            EvidenceQuality.HIGH.value: 0,
            EvidenceQuality.MEDIUM.value: 0,
            EvidenceQuality.LOW.value: 0
        }
        
        for item in items:
            if item.quality_score >= 0.7:
                distribution[EvidenceQuality.HIGH.value] += 1
            elif item.quality_score >= 0.4:
                distribution[EvidenceQuality.MEDIUM.value] += 1
            else:
                distribution[EvidenceQuality.LOW.value] += 1
        
        return distribution
    
    def filter_by_quality(
        self,
        ranking_result: RankingResult,
        min_quality: float = 0.5
    ) -> List[EvidenceItem]:
        """Filter evidence by minimum quality score."""
        return [e for e in ranking_result.ranked_evidence if e.quality_score >= min_quality]
    
    def get_evidence_summary(self, ranking_result: RankingResult) -> Dict[str, Any]:
        """Get summary of evidence ranking."""
        return {
            'total_evidence': len(ranking_result.ranked_evidence),
            'top_evidence_count': len(ranking_result.top_evidence),
            'avg_quality_score': ranking_result.avg_quality_score,
            'quality_distribution': ranking_result.quality_distribution,
            'processing_time_ms': ranking_result.processing_time_ms,
            'high_quality_count': ranking_result.quality_distribution.get('high', 0)
        }


# Factory functions
def create_evidence_ranker(
    relevance_weight: float = 0.35,
    authority_weight: float = 0.25,
    freshness_weight: float = 0.20,
    completeness_weight: float = 0.20
) -> EvidenceRanker:
    """Create evidence ranker instance."""
    return EvidenceRanker(relevance_weight, authority_weight, freshness_weight, completeness_weight)


def rank_evidence(
    evidence_items: List[Dict[str, Any]],
    query: str,
    top_k: int = 5
) -> RankingResult:
    """Convenience function to rank evidence."""
    ranker = EvidenceRanker()
    return ranker.rank_evidence(evidence_items, query, top_k=top_k)
