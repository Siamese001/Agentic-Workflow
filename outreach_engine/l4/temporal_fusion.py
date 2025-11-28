"""
Temporal rank fusion for temporal KG - Phase 6 L4 expansion.

Implements deterministic fusion of hybrid, KG, and temporal scores
with deterministic tie-break rules.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


class TemporalRankFusion:
    """
    Implements deterministic temporal rank fusion.
    
    Combines hybrid search scores, KG traversal scores, and temporal weights
    using the formula: fused = 0.5*hybrid + 0.3*kg + 0.2*temporal
    with deterministic tie-break rules for equal scores.
    """
    
    def __init__(self):
        """Initialize temporal rank fusion with default weights."""
        self.hybrid_weight = 0.5
        self.kg_weight = 0.3
        self.temporal_weight = 0.2
        
        # Source priority for tie-breaking (lower number = higher priority)
        self.source_priorities = {
            "hybrid": 1,
            "kg": 2, 
            "temporal": 3,
            "unknown": 999
        }
    
    def fuse(self, hybrid_scores: List[float], kg_scores: List[float], temporal_scores: List[float]) -> List[float]:
        """
        Fuse scores from hybrid search, KG traversal, and temporal weighting.
        
        Args:
            hybrid_scores: List of hybrid search scores (0-1)
            kg_scores: List of KG traversal scores (0-1)
            temporal_scores: List of temporal weight scores (0-1)
            
        Returns:
            List of fused scores (0-1)
        """
        # Early return: if only hybrid scores exist, return unchanged
        if hybrid_scores and not kg_scores and not temporal_scores:
            return hybrid_scores.copy()
        
        # Normalize input scores to 0-1 range
        normalized_hybrid = self._normalize_scores(hybrid_scores)
        normalized_kg = self._normalize_scores(kg_scores)
        normalized_temporal = self._normalize_scores(temporal_scores)
        
        # Determine maximum length
        max_length = max(len(normalized_hybrid), len(normalized_kg), len(normalized_temporal))
        
        # Pad shorter lists with zeros
        padded_hybrid = normalized_hybrid + [0.0] * (max_length - len(normalized_hybrid))
        padded_kg = normalized_kg + [0.0] * (max_length - len(normalized_kg))
        padded_temporal = normalized_temporal + [0.0] * (max_length - len(normalized_temporal))
        
        # Apply fusion formula
        fused_scores = []
        for i in range(max_length):
            fused_score = (
                self.hybrid_weight * padded_hybrid[i] +
                self.kg_weight * padded_kg[i] +
                self.temporal_weight * padded_temporal[i]
            )
            fused_scores.append(fused_score)
        
        return fused_scores
    
    def fuse_with_metadata(self, hybrid_scores: List[float], kg_scores: List[float], 
                           temporal_scores: List[float], metadata: Optional[List[dict]] = None) -> List[dict]:
        """
        Fuse scores with metadata preservation.
        
        Args:
            hybrid_scores: List of hybrid search scores
            kg_scores: List of KG traversal scores  
            temporal_scores: List of temporal weight scores
            metadata: Optional metadata list to preserve with fused scores
            
        Returns:
            List of dictionaries with fused scores and metadata
        """
        fused_scores = self.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        if metadata is None:
            return [{"score": score} for score in fused_scores]
        
        # Ensure metadata length matches fused scores
        max_length = len(fused_scores)
        padded_metadata = metadata + [{}] * (max_length - len(metadata))
        
        result = []
        for i, score in enumerate(fused_scores):
            result.append({
                "score": score,
                "metadata": padded_metadata[i]
            })
        
        return result
    
    def fuse_with_tiebreak(self, hybrid_scores: List[float], kg_scores: List[float], 
                          temporal_scores: List[float], metadata: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Fuse scores with deterministic tie-break rules.
        
        Args:
            hybrid_scores: List of hybrid search scores
            kg_scores: List of KG traversal scores  
            temporal_scores: List of temporal weight scores
            metadata: Optional metadata list containing timestamps and sources
            
        Returns:
            List of dictionaries with fused scores, sorted by tie-break rules
        """
        # Get basic fused scores
        fused_scores = self.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        if metadata is None:
            metadata = [{}] * len(fused_scores)
        
        # Ensure metadata length matches and handle None values
        max_length = len(fused_scores)
        # Replace None items with empty dicts
        clean_metadata = [(m if m is not None else {}) for m in metadata] if metadata else []
        padded_metadata = clean_metadata + [{}] * (max_length - len(clean_metadata))
        
        # Ensure all metadata items have default keys for tie-breaking
        for i, meta in enumerate(padded_metadata):
            if 'source' not in meta:
                meta['source'] = 'unknown'
            if 'timestamp' not in meta:
                meta['timestamp'] = datetime.min.replace(tzinfo=UTC)
        
        # Create list of tuples for sorting with tie-break rules
        scored_items = []
        for i, score in enumerate(fused_scores):
            item_metadata = padded_metadata[i] if i < len(padded_metadata) else {}
            
            # Extract tie-break criteria
            timestamp = item_metadata.get('timestamp', datetime.min.replace(tzinfo=UTC))
            source = item_metadata.get('source', 'unknown')
            source_priority = self.source_priorities.get(source, 999)
            
            # Create tie-break tuple: (-score, source_priority, -timestamp)
            # Negative score for descending order, negative timestamp for recent first
            tie_break_tuple = (-score, source_priority, -timestamp.timestamp() if timestamp else 0)
            
            scored_items.append({
                'score': score,
                'metadata': item_metadata,
                'tie_break_tuple': tie_break_tuple
            })
        
        # Sort by tie-break rules (deterministic)
        scored_items.sort(key=lambda x: x['tie_break_tuple'])
        
        # Remove tie-break tuples from final result
        return [{'score': item['score'], 'metadata': item['metadata']} for item in scored_items]
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to 0-1 range.
        
        Args:
            scores: List of scores to normalize
            
        Returns:
            Normalized scores
        """
        if not scores:
            return []
        
        # Clamp scores to 0-1 range first
        clamped_scores = [max(0.0, min(1.0, score)) for score in scores]
        
        # If all scores are already in 0-1 range, return as-is
        if all(0.0 <= score <= 1.0 for score in clamped_scores):
            return clamped_scores
        
        # Find min and max for linear normalization
        min_score = min(clamped_scores)
        max_score = max(clamped_scores)
        
        if max_score == min_score:
            # All scores are the same, return normalized to 0.5
            return [0.5] * len(clamped_scores)
        
        # Linear normalization to 0-1 range
        normalized = []
        for score in clamped_scores:
            normalized_score = (score - min_score) / (max_score - min_score)
            normalized.append(normalized_score)
        
        return normalized
    
    def set_weights(self, hybrid_weight: float, kg_weight: float, temporal_weight: float) -> None:
        """
        Set custom fusion weights.
        
        Args:
            hybrid_weight: Weight for hybrid search scores (0-1)
            kg_weight: Weight for KG traversal scores (0-1)
            temporal_weight: Weight for temporal scores (0-1)
        """
        # Normalize weights to sum to 1
        total_weight = hybrid_weight + kg_weight + temporal_weight
        
        if total_weight == 0:
            # Default weights if all are zero
            self.hybrid_weight = 0.5
            self.kg_weight = 0.3
            self.temporal_weight = 0.2
        else:
            self.hybrid_weight = hybrid_weight / total_weight
            self.kg_weight = kg_weight / total_weight
            self.temporal_weight = temporal_weight / total_weight
    
    def get_weights(self) -> dict:
        """
        Get current fusion weights.
        
        Returns:
            Dictionary with current weights
        """
        return {
            "hybrid_weight": self.hybrid_weight,
            "kg_weight": self.kg_weight,
            "temporal_weight": self.temporal_weight
        }
