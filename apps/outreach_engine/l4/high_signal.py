"""
High signal scoring for temporal KG - Phase 6 L4 expansion.

Implements signal detection for numeric mentions, product launches, hiring trends, and strategy pivots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import re
import logging

if TYPE_CHECKING:
    from l4.temporal_kg import TemporalNodeMetadata

logger = logging.getLogger(__name__)


@dataclass
class HighSignalScore:
    """Represents a high signal score with rationale."""
    score: float
    rationale: str


class HighSignalScorer:
    """Scores content based on high-signal indicators for outreach research."""
    
    def __init__(self):
        """Initialize high signal scorer with detection patterns."""
        # Numeric patterns
        self.numeric_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+[MKB]?',  # Monetary values
            r'\d+[MKB]?',  # Large numbers with units
            r'\d+x',  # Multipliers
            r'\d+(?:,\d{3})*(?:\.\d+)?'  # Numbers with thousands separators
        ]
        
        # High signal keywords
        self.product_launch_keywords = [
            'launched', 'released', 'introduced', 'debuted', 'unveiled',
            'product', 'platform', 'solution', 'technology', 'version'
        ]
        
        self.hiring_keywords = [
            'hiring', 'recruiting', 'expanding', 'workforce', 'talent',
            'job openings', 'positions', 'engineers', 'team', 'staff'
        ]
        
        self.strategy_keywords = [
            'pivoted', 'strategic', 'shift', 'changed', 'repositioning',
            'realignment', 'transformation', 'evolution', 'transition'
        ]
    
    def compute_signal_score(self, content: str, recency_weight: float = 1.0) -> HighSignalScore:
        """
        Compute high signal score for content.
        
        Args:
            content: Text content to score
            recency_weight: Temporal weight to apply multiplicatively
            
        Returns:
            HighSignalScore with score and rationale
        """
        score = 0.0
        rationale_parts = []
        
        # Check for numeric mentions
        numeric_score = self._detect_numeric_mentions(content)
        if numeric_score > 0:
            score += numeric_score
            rationale_parts.append("Contains numeric metrics")
        
        # Check for product launches
        launch_score = self._detect_product_launches(content)
        if launch_score > 0:
            score += launch_score
            rationale_parts.append("Product launch mentioned")
        
        # Check for hiring trends
        hiring_score = self._detect_hiring_trends(content)
        if hiring_score > 0:
            score += hiring_score
            rationale_parts.append("Hiring trends detected")
        
        # Check for strategy pivots
        strategy_score = self._detect_strategy_pivots(content)
        if strategy_score > 0:
            score += strategy_score
            rationale_parts.append("Strategy pivot indicated")
        
        # Normalize score to 0-1 range (individual signals should be high)
        normalized_score = min(score, 1.0)  # Clamp to 1.0, don't divide by 4.0
        
        # Apply recency weight multiplicatively
        final_score = normalized_score * recency_weight
        
        # Clamp to 0-1 range
        final_score = max(0.0, min(1.0, final_score))
        
        rationale = "; ".join(rationale_parts) if rationale_parts else "No high-signal indicators detected"
        
        return HighSignalScore(score=final_score, rationale=rationale)
    
    def compute_signal_score_with_metadata(self, content: str, metadata: TemporalNodeMetadata) -> HighSignalScore:
        """
        Compute signal score using temporal metadata.
        
        Args:
            content: Text content to score
            metadata: TemporalNodeMetadata with temporal information
            
        Returns:
            HighSignalScore with score and rationale
        """
        # Apply hop distance penalty to recency weight
        adjusted_weight = self._apply_hop_distance_to_weight(metadata.weight, metadata.hop_distance)
        
        return self.compute_signal_score(content, adjusted_weight)
    
    def _detect_numeric_mentions(self, content: str) -> float:
        """Detect numeric mentions and return signal score."""
        content_lower = content.lower()
        
        for pattern in self.numeric_patterns:
            if re.search(pattern, content_lower):
                return 1.0  # Strong signal for any numeric mention
        
        return 0.0
    
    def _detect_product_launches(self, content: str) -> float:
        """Detect product launch mentions and return signal score."""
        content_lower = content.lower()
        
        launch_count = sum(1 for keyword in self.product_launch_keywords if keyword in content_lower)
        
        if launch_count >= 2:
            return 1.0  # Strong signal
        elif launch_count == 1:
            return 0.8  # Moderate signal
        
        return 0.0
    
    def _detect_hiring_trends(self, content: str) -> float:
        """Detect hiring trend mentions and return signal score."""
        content_lower = content.lower()
        
        hiring_count = sum(1 for keyword in self.hiring_keywords if keyword in content_lower)
        
        if hiring_count >= 2:
            return 0.8  # Strong signal
        elif hiring_count == 1:
            return 0.6  # Moderate signal
        
        return 0.0
    
    def _detect_strategy_pivots(self, content: str) -> float:
        """Detect strategy pivot mentions and return signal score."""
        content_lower = content.lower()
        
        strategy_count = sum(1 for keyword in self.strategy_keywords if keyword in content_lower)
        
        if strategy_count >= 2:
            return 0.9  # Strong signal
        elif strategy_count == 1:
            return 0.7  # Moderate signal
        
        return 0.0
    
    def _apply_hop_distance_to_weight(self, base_weight: float, hop_distance: int) -> float:
        """Apply hop distance penalty to weight."""
        if hop_distance == 0:
            return base_weight
        elif hop_distance == 1:
            return base_weight * 0.9
        elif hop_distance == 2:
            return base_weight * 0.7
        elif hop_distance == 3:
            return base_weight * 0.5
        else:
            return base_weight * 0.3  # Maximum penalty for >3 hops
