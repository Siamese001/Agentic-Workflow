"""LIC Signal Scoring - L4 deterministic scoring for LIC research results.

Implements nuclear prompt requirements for deterministic signal scoring:
- Score LIC research results for relevance and strength
- L4 only: deterministic scoring, no LLM
- Simple scoring based on recency, source type, keyword overlap
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class LICSignalScore:
    """Scored research signal with relevance metrics."""
    signal_id: str                       # original signal identifier
    text: str                           # signal text content
    relevance_score: float              # overall relevance score [0, 1]
    recency_score: float                # recency-based score [0, 1]
    source_score: float                 # source credibility score [0, 1]
    keyword_score: float                # keyword overlap score [0, 1]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICSignalScoring:
    """L4 deterministic scorer for LIC research signals.
    
    Scores research results based on recency, source type,
    and keyword overlap with role/company/themes.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC signal scorer."""
        self.telemetry_bus = telemetry_bus
        
        # Source credibility weights
        self.source_weights = {
            "official": 0.9,      # company website, press releases
            "news": 0.8,          # reputable news sources
            "blog": 0.6,          # company blog, technical blog
            "social": 0.4,        # social media posts
            "forum": 0.3,         # forum discussions
            "random": 0.2,        # random web content
        }
        
        # Recency decay parameters
        self.recency_threshold_days = 365  # 1 year
        self.recency_half_life_days = 90   # 3 months
        
        # Keyword importance weights
        self.keyword_weights = {
            "company_name": 0.4,
            "role_title": 0.3,
            "strategic_themes": 0.2,
            "technical_terms": 0.1,
        }
    
    def score(self, raw_results: List[Dict[str, Any]]) -> List[LICSignalScore]:
        """Score raw research results for relevance and strength.
        
        Args:
            raw_results: List of raw research results from vector search
            
        Returns:
            List of scored signals with relevance metrics
        """
        if not raw_results:
            return []
        
        scored_signals = []
        
        for result in raw_results:
            # Extract signal data
            signal_id = result.get("id", "")
            text = result.get("text", result.get("content", ""))
            metadata = result.get("metadata", {})
            
            # Calculate component scores
            recency_score = self._calculate_recency_score(metadata)
            source_score = self._calculate_source_score(metadata)
            keyword_score = self._calculate_keyword_score(text, metadata)
            
            # Calculate overall relevance score
            relevance_score = self._calculate_overall_score(
                recency_score, source_score, keyword_score
            )
            
            # Create scored signal
            scored_signal = LICSignalScore(
                signal_id=signal_id,
                text=text,
                relevance_score=relevance_score,
                recency_score=recency_score,
                source_score=source_score,
                keyword_score=keyword_score,
                metadata={
                    "original_metadata": metadata,
                    "scoring_timestamp": datetime.now().isoformat(),
                },
            )
            
            scored_signals.append(scored_signal)
        
        # Sort by relevance score (highest first)
        scored_signals.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Record telemetry (best-effort)
        self._safe_record_telemetry(scored_signals)
        
        return scored_signals
    
    def _calculate_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score based on publication date."""
        timestamp_str = metadata.get("timestamp", metadata.get("date", ""))
        
        if not timestamp_str:
            # No timestamp - assume old content
            return 0.3
        
        try:
            # Parse timestamp (handle various formats)
            if isinstance(timestamp_str, str):
                # Try ISO format first
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    # Try other common formats
                    timestamp = datetime.strptime(timestamp_str[:10], '%Y-%m-%d')
            else:
                # Assume it's already a datetime
                timestamp = timestamp_str
            
            # Calculate age in days
            age_days = (datetime.now() - timestamp).days
            
            # Apply exponential decay
            if age_days <= 0:
                return 1.0
            elif age_days >= self.recency_threshold_days:
                return 0.1
            else:
                # Exponential decay based on half-life
                decay_factor = 0.5 ** (age_days / self.recency_half_life_days)
                return max(0.1, decay_factor)
        
        except Exception:
            # Failed to parse timestamp - assume old content
            logger.debug(f"Failed to parse timestamp: {timestamp_str}")
            return 0.3
    
    def _calculate_source_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate source credibility score."""
        source_type = metadata.get("source_type", metadata.get("source", "random")).lower()
        
        # Map source type to credibility weight
        for source_pattern, weight in self.source_weights.items():
            if source_pattern in source_type:
                return weight
        
        # Unknown source type - default to low credibility
        return 0.2
    
    def _calculate_keyword_score(self, text: str, metadata: Dict[str, Any]) -> float:
        """Calculate keyword overlap score."""
        text_lower = text.lower()
        total_score = 0.0
        total_weight = 0.0
        
        # Score company name overlap
        company_name = metadata.get("company_name", "").lower()
        if company_name:
            weight = self.keyword_weights["company_name"]
            if company_name in text_lower:
                total_score += weight
            total_weight += weight
        
        # Score role title overlap
        role_title = metadata.get("role_title", "").lower()
        if role_title:
            weight = self.keyword_weights["role_title"]
            role_keywords = role_title.split()
            keyword_matches = sum(1 for kw in role_keywords if kw in text_lower)
            if role_keywords:
                match_ratio = keyword_matches / len(role_keywords)
                total_score += weight * match_ratio
            total_weight += weight
        
        # Score strategic themes overlap
        strategic_themes = metadata.get("strategic_themes", [])
        if strategic_themes:
            weight = self.keyword_weights["strategic_themes"]
            theme_matches = sum(1 for theme in strategic_themes if theme.lower() in text_lower)
            if strategic_themes:
                match_ratio = theme_matches / len(strategic_themes)
                total_score += weight * match_ratio
            total_weight += weight
        
        # Score technical terms overlap
        technical_terms = self._extract_technical_terms(text_lower)
        if technical_terms:
            weight = self.keyword_weights["technical_terms"]
            # Bonus for having technical terms (simple heuristic)
            tech_bonus = min(len(technical_terms) * 0.1, weight)
            total_score += tech_bonus
            total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.1  # Minimum score for any content
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text."""
        technical_indicators = [
            "ai", "ml", "machine learning", "artificial intelligence",
            "cloud", "aws", "azure", "gcp", "kubernetes", "docker",
            "python", "java", "javascript", "react", "angular",
            "microservices", "api", "database", "sql", "nosql",
            "devops", "ci/cd", "agile", "scrum", "saas",
            "infrastructure", "architecture", "scalability",
            "performance", "optimization", "security", "privacy"
        ]
        
        found_terms = []
        for term in technical_indicators:
            if term in text:
                found_terms.append(term)
        
        return found_terms
    
    def _calculate_overall_score(
        self,
        recency_score: float,
        source_score: float,
        keyword_score: float,
    ) -> float:
        """Calculate overall relevance score from component scores."""
        # Weight the components
        weights = {
            "recency": 0.3,
            "source": 0.3,
            "keyword": 0.4,
        }
        
        overall_score = (
            recency_score * weights["recency"] +
            source_score * weights["source"] +
            keyword_score * weights["keyword"]
        )
        
        return round(overall_score, 3)
    
    def _safe_record_telemetry(self, scored_signals: List[LICSignalScore]) -> None:
        """Record telemetry event safely without breaking scoring."""
        if not self.telemetry_bus:
            return
        
        try:
            if scored_signals:
                avg_score = sum(s.relevance_score for s in scored_signals) / len(scored_signals)
                max_score = max(s.relevance_score for s in scored_signals)
                min_score = min(s.relevance_score for s in scored_signals)
            else:
                avg_score = max_score = min_score = 0.0
            
            self.telemetry_bus.record_event(
                "lic_signal_scoring_completed",
                layer="L4",
                payload={
                    "signals_scored": len(scored_signals),
                    "avg_relevance_score": avg_score,
                    "max_relevance_score": max_score,
                    "min_relevance_score": min_score,
                },
            )
        except Exception:
            # Telemetry failures should never break scoring logic
            logger.debug("Failed to record telemetry for LIC signal scoring")
