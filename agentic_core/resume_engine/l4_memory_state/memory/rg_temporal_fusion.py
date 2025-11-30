from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class RankedResult:
    """Represents a ranked search result."""
    item_id: str
    score: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TemporalRankFusion:
    """Minimal functional temporal rank fusion implementation."""

    def __init__(self, decay_factor: float = 0.9):
        self.decay_factor = decay_factor

    def process(self, *args, **kwargs) -> Any:
        """Process temporal rank fusion on result lists."""
        result_lists = kwargs.get("result_lists", [])
        if not result_lists:
            return {"fused_results": [], "processed": True}
        
        fused_results = self.fuse_rankings(result_lists)
        return {
            "fused_results": [
                {
                    "item_id": r.item_id,
                    "fused_score": r.score,
                    "timestamp": r.timestamp.isoformat()
                } for r in fused_results
            ],
            "processed": True,
            "total_results": len(fused_results)
        }

    def fuse_rankings(self, result_lists: List[List[RankedResult]]) -> List[RankedResult]:
        """Fuse multiple ranked result lists using temporal decay."""
        if not result_lists:
            return []
        
        # Collect all unique items
        item_scores = {}
        item_metadata = {}
        
        for results in result_lists:
            for i, result in enumerate(results):
                if result.item_id not in item_scores:
                    item_scores[result.item_id] = 0.0
                    item_metadata[result.item_id] = result.metadata
                
                # Apply rank-based scoring with temporal decay
                rank_score = 1.0 / (i + 1)  # Reciprocal rank
                time_factor = self._calculate_time_factor(result.timestamp)
                combined_score = rank_score * time_factor
                
                item_scores[result.item_id] += combined_score
        
        # Sort by fused score
        fused_results = []
        for item_id, score in item_scores.items():
            fused_results.append(RankedResult(
                item_id=item_id,
                score=score,
                timestamp=datetime.now(),
                metadata=item_metadata[item_id]
            ))
        
        return sorted(fused_results, key=lambda x: x.score, reverse=True)

    def _calculate_time_factor(self, timestamp: datetime) -> float:
        """Calculate temporal decay factor."""
        now = datetime.now()
        time_diff = (now - timestamp).total_seconds()
        
        # Apply exponential decay based on time difference
        if time_diff < 0:
            return 1.0  # Future timestamps get full weight
        
        # Decay over days (86400 seconds per day)
        days_passed = time_diff / 86400
        return math.pow(self.decay_factor, days_passed)

    def add_temporal_boost(self, results: List[RankedResult], 
                          boost_factor: float = 1.2) -> List[RankedResult]:
        """Apply temporal boost to recent results."""
        now = datetime.now()
        
        for result in results:
            time_diff = (now - result.timestamp).total_seconds()
            if time_diff < 86400:  # Less than 1 day old
                result.score *= boost_factor
        
        return results
