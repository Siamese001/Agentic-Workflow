"""Pick Best Score - Utility for selecting best scores from collections.

This module provides utilities for selecting and ranking scores from collections,
including various selection strategies and tie-breaking mechanisms.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SelectionStrategy(Enum):
    """Strategies for selecting best scores."""
    MAX = "max"
    MIN = "min"
    TOP_K = "top_k"
    PERCENTILE = "percentile"
    THRESHOLD = "threshold"


class TieBreakMethod(Enum):
    """Methods for breaking ties."""
    FIRST = "first"
    LAST = "last"
    RANDOM = "random"
    METADATA = "metadata"


@dataclass
class ScoreEntry:
    """Individual score entry with metadata."""
    id: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None


@dataclass
class SelectionCriteria:
    """Criteria for score selection."""
    strategy: SelectionStrategy = SelectionStrategy.MAX
    k: int = 1
    percentile: float = 90.0
    threshold: float = 0.5
    tie_break: TieBreakMethod = TieBreakMethod.FIRST
    metadata_key: Optional[str] = None


@dataclass
class SelectionResult:
    """Result of score selection."""
    selected: List[ScoreEntry]
    all_scores: List[ScoreEntry]
    criteria: SelectionCriteria
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PickBestScoreConfig:
    """Configuration for pick best score operations."""
    default_strategy: SelectionStrategy = SelectionStrategy.MAX
    enable_logging: bool = True
    cache_results: bool = False


class PickBestScore:
    """Main class for picking best scores from collections."""

    def __init__(self, config: Optional[PickBestScoreConfig] = None):
        self.config = config or PickBestScoreConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {} if self.config.cache_results else None

    def pick_best(self, scores: List[ScoreEntry], criteria: Optional[SelectionCriteria] = None) -> SelectionResult:
        """Pick best scores based on criteria.
        
        Args:
            scores: List of score entries to evaluate
            criteria: Selection criteria (uses default if not provided)
            
        Returns:
            SelectionResult: Selected scores with metadata
        """
        criteria = criteria or SelectionCriteria(strategy=self.config.default_strategy)
        
        if self.config.enable_logging:
            self.logger.info(f"Picking best scores using strategy: {criteria.strategy.value}")
        
        try:
            # Validate input
            if not scores:
                return SelectionResult(
                    selected=[],
                    all_scores=[],
                    criteria=criteria,
                    metadata={"error": "No scores provided"}
                )
            
            # Sort scores
            sorted_scores = self._sort_scores(scores, criteria)
            
            # Apply selection strategy
            selected = self._apply_strategy(sorted_scores, criteria)
            
            # Handle ties if needed
            if criteria.strategy in [SelectionStrategy.MAX, SelectionStrategy.MIN]:
                selected = self._handle_ties(selected, criteria)
            
            result = SelectionResult(
                selected=selected,
                all_scores=scores,
                criteria=criteria,
                metadata={
                    "selected_at": datetime.utcnow().isoformat(),
                    "total_scores": len(scores),
                    "selected_count": len(selected),
                    "strategy": criteria.strategy.value
                }
            )
            
            if self.config.enable_logging:
                self.logger.info(f"Selected {len(selected)} scores from {len(scores)} total")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to pick best scores: {str(e)}")
            return SelectionResult(
                selected=[],
                all_scores=scores,
                criteria=criteria,
                metadata={"error": str(e)}
            )

    def pick_best_simple(self, scores: List[float], strategy: str = "max", k: int = 1) -> List[float]:
        """Simple version that works with raw scores.
        
        Args:
            scores: List of raw scores
            strategy: Selection strategy
            k: Number of scores to select
            
        Returns:
            List[float]: Selected scores
        """
        # Convert to ScoreEntry objects
        score_entries = [
            ScoreEntry(id=str(i), score=score)
            for i, score in enumerate(scores)
        ]
        
        # Create criteria
        criteria = SelectionCriteria(
            strategy=SelectionStrategy(strategy),
            k=k
        )
        
        # Pick best
        result = self.pick_best(score_entries, criteria)
        
        # Extract scores
        return [entry.score for entry in result.selected]

    def get_top_k(self, scores: List[ScoreEntry], k: int, ascending: bool = False) -> List[ScoreEntry]:
        """Get top k scores.
        
        Args:
            scores: List of score entries
            k: Number of scores to return
            ascending: If True, return lowest scores
            
        Returns:
            List[ScoreEntry]: Top k scores
        """
        strategy = SelectionStrategy.MIN if ascending else SelectionStrategy.MAX
        criteria = SelectionCriteria(strategy=strategy, k=k)
        
        result = self.pick_best(scores, criteria)
        return result.selected

    def filter_by_threshold(self, scores: List[ScoreEntry], threshold: float, 
                          above: bool = True) -> List[ScoreEntry]:
        """Filter scores by threshold.
        
        Args:
            scores: List of score entries
            threshold: Threshold value
            above: If True, keep scores above threshold
            
        Returns:
            List[ScoreEntry]: Filtered scores
        """
        criteria = SelectionCriteria(
            strategy=SelectionStrategy.THRESHOLD,
            threshold=threshold
        )
        
        result = self.pick_best(scores, criteria)
        
        if not above:
            # Invert selection
            selected_ids = set(s.id for s in result.selected)
            return [s for s in scores if s.id not in selected_ids]
        
        return result.selected

    def get_percentile(self, scores: List[ScoreEntry], percentile: float) -> List[ScoreEntry]:
        """Get scores at or above percentile.
        
        Args:
            scores: List of score entries
            percentile: Percentile threshold (0-100)
            
        Returns:
            List[ScoreEntry]: Scores at percentile
        """
        criteria = SelectionCriteria(
            strategy=SelectionStrategy.PERCENTILE,
            percentile=percentile
        )
        
        result = self.pick_best(scores, criteria)
        return result.selected

    def _sort_scores(self, scores: List[ScoreEntry], criteria: SelectionCriteria) -> List[ScoreEntry]:
        """Sort scores based on strategy."""
        reverse = True
        if criteria.strategy == SelectionStrategy.MIN:
            reverse = False
        
        # Sort by score, then by timestamp for tie-breaking
        sorted_scores = sorted(
            scores,
            key=lambda x: (x.score, x.timestamp or datetime.min),
            reverse=reverse
        )
        
        return sorted_scores

    def _apply_strategy(self, sorted_scores: List[ScoreEntry], criteria: SelectionCriteria) -> List[ScoreEntry]:
        """Apply selection strategy to sorted scores."""
        if criteria.strategy == SelectionStrategy.MAX:
            # Get max score(s)
            if sorted_scores:
                max_score = sorted_scores[0].score
                return [s for s in sorted_scores if s.score == max_score]
            return []
        
        elif criteria.strategy == SelectionStrategy.MIN:
            # Get min score(s)
            if sorted_scores:
                min_score = sorted_scores[0].score
                return [s for s in sorted_scores if s.score == min_score]
            return []
        
        elif criteria.strategy == SelectionStrategy.TOP_K:
            # Get top k scores
            return sorted_scores[:criteria.k]
        
        elif criteria.strategy == SelectionStrategy.PERCENTILE:
            # Get scores at percentile
            if not sorted_scores:
                return []
            
            index = int(len(sorted_scores) * (100 - criteria.percentile) / 100)
            return sorted_scores[index:]
        
        elif criteria.strategy == SelectionStrategy.THRESHOLD:
            # Get scores above/below threshold
            return [s for s in sorted_scores if s.score >= criteria.threshold]
        
        else:
            return sorted_scores

    def _handle_ties(self, scores: List[ScoreEntry], criteria: SelectionCriteria) -> List[ScoreEntry]:
        """Handle ties in score selection."""
        if len(scores) <= 1 or criteria.tie_break == TieBreakMethod.FIRST:
            return scores
        
        if criteria.tie_break == TieBreakMethod.LAST:
            return scores[-1:] if scores else []
        
        elif criteria.tie_break == TieBreakMethod.RANDOM:
            import random
            return [random.choice(scores)] if scores else []
        
        elif criteria.tie_break == TieBreakMethod.METADATA:
            if criteria.metadata_key:
                # Sort by metadata key
                sorted_by_metadata = sorted(
                    scores,
                    key=lambda x: x.metadata.get(criteria.metadata_key, ""),
                    reverse=True
                )
                return sorted_by_metadata[:1]
        
        return scores


# Factory function for easy instantiation
def create_pick_best_score(
    default_strategy: str = "max",
    enable_logging: bool = True,
    **kwargs
) -> PickBestScore:
    """Create a configured pick best score utility."""
    config = PickBestScoreConfig(
        default_strategy=SelectionStrategy(default_strategy),
        enable_logging=enable_logging,
        **kwargs
    )
    return PickBestScore(config)


# Convenience function for direct usage
def pick_best_score(
    scores: List[float],
    strategy: str = "max",
    k: int = 1,
    percentile: float = 90.0,
    threshold: float = 0.5
) -> List[float]:
    """Pick best scores from list.
    
    Args:
        scores: List of scores to evaluate
        strategy: Selection strategy
        k: Number of scores to select
        percentile: Percentile threshold
        threshold: Score threshold
        
    Returns:
        List[float]: Selected scores
    """
    picker = create_pick_best_score()
    
    # Convert to ScoreEntry objects
    score_entries = [
        ScoreEntry(id=str(i), score=score)
        for i, score in enumerate(scores)
    ]
    
    # Create criteria
    if strategy == "top_k":
        criteria = SelectionCriteria(strategy=SelectionStrategy.TOP_K, k=k)
    elif strategy == "percentile":
        criteria = SelectionCriteria(strategy=SelectionStrategy.PERCENTILE, percentile=percentile)
    elif strategy == "threshold":
        criteria = SelectionCriteria(strategy=SelectionStrategy.THRESHOLD, threshold=threshold)
    else:
        criteria = SelectionCriteria(strategy=SelectionStrategy(strategy))
    
    # Pick best
    result = picker.pick_best(score_entries, criteria)
    
    # Extract scores
    return [entry.score for entry in result.selected]
