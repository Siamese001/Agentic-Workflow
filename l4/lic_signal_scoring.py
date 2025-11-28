"""LIC Signal Scoring - L4 Memory/State Layer

Implements LIC-style signal scoring for research results.
Provides recency, diversity, and source quality scoring.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


logger = logging.getLogger(__name__)


@dataclass
class SignalScore:
    """Individual signal score component"""
    score_type: str
    value: float
    weight: float
    contribution: float


@dataclass
class SourceSignalMetrics:
    """Signal metrics for a single source"""
    source_id: str
    recency_score: float
    diversity_score: float
    quality_score: float
    relevance_score: float
    overall_signal: float


class SignalScorer:
    """
    L4 Signal Scoring Engine for LIC Intelligence
    
    Scores research sources based on recency, diversity, and quality
    metrics following LIC signal scoring methodology.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize signal scorer
        
        Args:
            config: Optional scoring configuration
        """
        self.config = config or self._get_default_config()
        
        # Scoring weights
        self.weights = self.config["scoring"]["weights"]
        
        # Time-based scoring parameters
        self.recency_params = self.config["scoring"]["recency"]
        
        # Quality scoring parameters
        self.quality_params = self.config["scoring"]["quality"]
        
        logger.info("SignalScorer initialized with LIC scoring methodology")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default scoring configuration"""
        return {
            "scoring": {
                "weights": {
                    "recency": 0.3,
                    "diversity": 0.2,
                    "quality": 0.3,
                    "relevance": 0.2
                },
                "recency": {
                    "max_age_days": 90,
                    "decay_rate": 0.05,
                    "freshness_bonus_days": 7
                },
                "quality": {
                    "source_type_weights": {
                        "company_intelligence": 0.9,
                        "news_article": 0.8,
                        "industry_report": 0.85,
                        "social_media": 0.6,
                        "forum_post": 0.5
                    },
                    "length_factor": {
                        "min_length": 100,
                        "optimal_length": 500,
                        "max_length": 2000
                    }
                },
                "diversity": {
                    "source_type_bonus": 0.1,
                    "domain_diversity_bonus": 0.15,
                    "temporal_spread_bonus": 0.1
                }
            }
        }
    
    async def score_sources(
        self,
        sources: List[Dict[str, Any]],
        plan: Any,
        recipient_company: str,
        recipient_archetype: str
    ) -> float:
        """
        Score a collection of research sources
        
        Args:
            sources: List of source dictionaries
            plan: Research plan (for context)
            recipient_company: Target company name
            recipient_archetype: Recipient archetype
            
        Returns:
            Overall signal score (0.0 to 1.0)
        """
        if not sources:
            return 0.0
        
        try:
            # Score individual sources
            source_metrics = []
            for source in sources:
                metrics = await self._score_single_source(source, recipient_company, recipient_archetype)
                source_metrics.append(metrics)
            
            # Calculate aggregate signal score
            overall_signal = self._calculate_aggregate_signal(source_metrics)
            
            logger.info(f"Signal scoring completed for {len(sources)} sources: {overall_signal:.3f}")
            
            return overall_signal
            
        except Exception as e:
            logger.error(f"Signal scoring failed: {str(e)}")
            return 0.0
    
    async def _score_single_source(
        self,
        source: Dict[str, Any],
        recipient_company: str,
        recipient_archetype: str
    ) -> SourceSignalMetrics:
        """Score a single source across all dimensions"""
        
        # Extract source information
        source_id = source.get("id", "unknown")
        text = source.get("text", "")
        metadata = source.get("metadata", {})
        
        # Calculate individual scores
        recency_score = self._calculate_recency_score(metadata)
        quality_score = self._calculate_quality_score(source, metadata)
        relevance_score = self._calculate_relevance_score(text, metadata, recipient_company, recipient_archetype)
        diversity_score = self._calculate_diversity_score(source, metadata)
        
        # Calculate overall signal
        overall_signal = (
            recency_score * self.weights["recency"] +
            quality_score * self.weights["quality"] +
            relevance_score * self.weights["relevance"] +
            diversity_score * self.weights["diversity"]
        )
        
        return SourceSignalMetrics(
            source_id=source_id,
            recency_score=recency_score,
            quality_score=quality_score,
            relevance_score=relevance_score,
            diversity_score=diversity_score,
            overall_signal=overall_signal
        )
    
    def _calculate_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score based on source age"""
        
        # Get source date
        source_date_str = metadata.get("retrieved_at") or metadata.get("published_at")
        
        if not source_date_str:
            # Default to moderate recency for undated sources
            return 0.5
        
        try:
            # Parse date
            if isinstance(source_date_str, str):
                source_date = datetime.fromisoformat(source_date_str.replace('Z', '+00:00'))
            else:
                source_date = source_date_str
            
            # Calculate age in days
            age_days = (datetime.now() - source_date).days
            
            # Apply recency scoring
            max_age = self.recency_params["max_age_days"]
            decay_rate = self.recency_params["decay_rate"]
            freshness_bonus = self.recency_params["freshness_bonus_days"]
            
            if age_days <= freshness_bonus:
                # Fresh sources get bonus
                return 1.0
            elif age_days <= max_age:
                # Decay score with age
                effective_age = age_days - freshness_bonus
                decayed_score = 1.0 - (effective_age * decay_rate)
                return max(decayed_score, 0.1)
            else:
                # Very old sources get minimum score
                return 0.1
                
        except Exception as e:
            logger.warning(f"Failed to calculate recency score: {str(e)}")
            return 0.5
    
    def _calculate_quality_score(self, source: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate quality score based on source characteristics"""
        
        # Base quality from source type
        source_type = metadata.get("source_type", "unknown")
        source_type_weight = self.quality_params["source_type_weights"].get(source_type, 0.5)
        
        # Length factor
        text = source.get("text", "")
        length_score = self._calculate_length_score(text)
        
        # Content quality indicators
        content_score = self._calculate_content_quality_score(text)
        
        # Metadata completeness
        metadata_score = self._calculate_metadata_score(metadata)
        
        # Combine quality factors
        quality_score = (
            source_type_weight * 0.4 +
            length_score * 0.2 +
            content_score * 0.3 +
            metadata_score * 0.1
        )
        
        return min(quality_score, 1.0)
    
    def _calculate_length_score(self, text: str) -> float:
        """Calculate score based on content length"""
        text_length = len(text)
        
        min_length = self.quality_params["length_factor"]["min_length"]
        optimal_length = self.quality_params["length_factor"]["optimal_length"]
        max_length = self.quality_params["length_factor"]["max_length"]
        
        if text_length < min_length:
            # Too short gets penalty
            return text_length / min_length
        elif text_length <= optimal_length:
            # Optimal length gets full score
            return 1.0
        elif text_length <= max_length:
            # Longer than optimal but acceptable
            excess_ratio = (text_length - optimal_length) / (max_length - optimal_length)
            return 1.0 - (excess_ratio * 0.3)  # Max 30% penalty
        else:
            # Too long gets bigger penalty
            excess_ratio = (text_length - max_length) / max_length
            return max(0.3, 0.7 - (excess_ratio * 0.5))  # Min 30% score
    
    def _calculate_content_quality_score(self, text: str) -> float:
        """Calculate content quality based on text characteristics"""
        
        if not text:
            return 0.0
        
        score = 0.5  # Base score
        
        # Check for professional language indicators
        professional_indicators = [
            "strategy", "analysis", "research", "development", "innovation",
            "performance", "results", "impact", "growth", "success"
        ]
        
        professional_count = sum(1 for indicator in professional_indicators if indicator.lower() in text.lower())
        if professional_count > 0:
            score += min(professional_count * 0.05, 0.2)
        
        # Check for data/numbers (indicates factual content)
        if re.search(r'\d+%|\$\d+|\d+\.\d+', text):
            score += 0.1
        
        # Check for structured content (headings, lists)
        if re.search(r'^#+\s|^-\s|\*\s', text, re.MULTILINE):
            score += 0.1
        
        # Penalty for excessive repetition
        words = text.lower().split()
        if len(set(words)) / len(words) < 0.5:  # Less than 50% unique words
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _calculate_metadata_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate score based on metadata completeness"""
        
        required_fields = ["source_type", "retrieved_at"]
        optional_fields = ["author", "title", "source_url", "company_name"]
        
        # Check required fields
        required_score = sum(1 for field in required_fields if field in metadata) / len(required_fields)
        
        # Check optional fields
        optional_score = sum(1 for field in optional_fields if field in metadata) / len(optional_fields)
        
        # Combine with higher weight on required fields
        metadata_score = required_score * 0.7 + optional_score * 0.3
        
        return metadata_score
    
    def _calculate_relevance_score(
        self,
        text: str,
        metadata: Dict[str, Any],
        recipient_company: str,
        recipient_archetype: str
    ) -> float:
        """Calculate relevance score to recipient and context"""
        
        if not text:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Company name relevance
        if recipient_company.lower() in text_lower:
            score += 0.4
        
        # Archetype-specific keywords
        archetype_keywords = {
            "executive": ["strategic", "business", "leadership", "growth", "market"],
            "hiring_manager": ["team", "hiring", "recruitment", "talent", "management"],
            "technical_lead": ["technical", "engineering", "development", "architecture", "innovation"],
            "recruiter": ["opportunity", "career", "candidate", "position", "role"]
        }
        
        keywords = archetype_keywords.get(recipient_archetype, [])
        keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
        if keyword_matches > 0:
            score += min(keyword_matches * 0.1, 0.3)
        
        # Industry/business relevance indicators
        business_indicators = ["company", "business", "organization", "enterprise", "corporation"]
        business_matches = sum(1 for indicator in business_indicators if indicator in text_lower)
        if business_matches > 0:
            score += min(business_matches * 0.05, 0.2)
        
        return min(score, 1.0)
    
    def _calculate_diversity_score(self, source: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate diversity score (placeholder for more complex diversity analysis)"""
        
        # Base diversity score
        diversity_score = 0.7
        
        # Source type diversity bonus
        source_type = metadata.get("source_type", "unknown")
        if source_type in ["news_article", "industry_report", "company_intelligence"]:
            diversity_score += self.config["scoring"]["diversity"]["source_type_bonus"]
        
        # Domain diversity (simplified)
        source_url = metadata.get("source_url", "")
        if source_url and any(domain in source_url for domain in ["techcrunch.com", "forbes.com", "reuters.com"]):
            diversity_score += self.config["scoring"]["diversity"]["domain_diversity_bonus"]
        
        return min(diversity_score, 1.0)
    
    def _calculate_aggregate_signal(self, source_metrics: List[SourceSignalMetrics]) -> float:
        """Calculate aggregate signal score from multiple sources"""
        
        if not source_metrics:
            return 0.0
        
        # Weight sources by their individual signal scores
        total_weight = 0.0
        weighted_signal = 0.0
        
        for metrics in source_metrics:
            weight = metrics.overall_signal  # Use individual signal as weight
            total_weight += weight
            weighted_signal += metrics.overall_signal * weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate weighted average
        aggregate_signal = weighted_signal / total_weight
        
        # Apply diversity bonus for multiple sources
        if len(source_metrics) > 1:
            diversity_bonus = min(len(source_metrics) * 0.02, 0.1)  # Max 10% bonus
            aggregate_signal = min(aggregate_signal + diversity_bonus, 1.0)
        
        return aggregate_signal
    
    async def get_source_ranking(
        self,
        sources: List[Dict[str, Any]],
        recipient_company: str,
        recipient_archetype: str
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Get ranked list of sources by signal score
        
        Args:
            sources: List of source dictionaries
            recipient_company: Target company name
            recipient_archetype: Recipient archetype
            
        Returns:
            List of (source, score) tuples sorted by score (highest first)
        """
        
        source_scores = []
        
        for source in sources:
            metrics = await self._score_single_source(source, recipient_company, recipient_archetype)
            source_scores.append((source, metrics.overall_signal))
        
        # Sort by signal score (highest first)
        source_scores.sort(key=lambda x: x[1], reverse=True)
        
        return source_scores
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Get current scoring weights"""
        return self.weights.copy()
    
    def update_scoring_weights(self, new_weights: Dict[str, float]):
        """Update scoring weights"""
        # Validate weights sum to 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total_weight}")
        
        self.weights.update(new_weights)
        logger.info(f"Updated scoring weights: {self.weights}")
