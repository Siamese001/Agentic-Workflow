"""
Temporal tie-break behavior tests - Phase 6 L4 expansion.

Tests deterministic tie-break rules in TemporalRankFusion:
- Numeric ordering precedence
- Source priority ordering
- Timestamp priority ordering
- Deterministic sorting consistency
- Edge cases for tie-breaking
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, patch

from l4.temporal_fusion import TemporalRankFusion


class TestTemporalTieBreak:
    """Test suite for temporal tie-break behavior in TemporalRankFusion."""
    
    def setup_method(self):
        """Set up test fixtures for tie-break testing."""
        self.temporal_fusion = TemporalRankFusion()
        self.now = datetime.now(UTC)
        
        # Test data with equal scores for tie-break testing
        self.equal_scores = [0.8, 0.8, 0.8, 0.8]
        
        # Test metadata with different sources and timestamps
        self.test_metadata = [
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=1),
                'index': 0
            },
            {
                'source': 'kg',
                'timestamp': self.now - timedelta(days=2),
                'index': 1
            },
            {
                'source': 'temporal',
                'timestamp': self.now - timedelta(days=3),
                'index': 2
            },
            {
                'source': 'unknown',
                'timestamp': self.now - timedelta(days=4),
                'index': 3
            }
        ]
    
    def test_tie_break_numeric_ordering(self):
        """Test tie-break with different numeric scores (primary sort)."""
        scores = [0.9, 0.8, 0.7, 0.6]
        metadata = self.test_metadata
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            scores, [], [], metadata
        )
        
        # Should be sorted by score descending
        assert len(result) == 4
        assert result[0]['score'] == 0.9
        assert result[1]['score'] == 0.8
        assert result[2]['score'] == 0.7
        assert result[3]['score'] == 0.6
    
    def test_tie_break_source_priority(self):
        """Test tie-break with source priority ordering."""
        scores = self.equal_scores
        metadata = self.test_metadata
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            scores, [], [], metadata
        )
        
        # Should be sorted by source priority: hybrid(1) < kg(2) < temporal(3) < unknown(999)
        assert len(result) == 4
        assert result[0]['metadata']['source'] == 'hybrid'
        assert result[1]['metadata']['source'] == 'kg'
        assert result[2]['metadata']['source'] == 'temporal'
        assert result[3]['metadata']['source'] == 'unknown'
    
    def test_tie_break_timestamp_priority(self):
        """Test tie-break with timestamp priority (recent first)."""
        scores = self.equal_scores
        
        # Same source with different timestamps
        same_source_metadata = [
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=3),  # Oldest
                'index': 0
            },
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=1),  # Newest
                'index': 1
            },
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=2),  # Middle
                'index': 2
            }
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            scores[:3], [], [], same_source_metadata
        )
        
        # Should be sorted by timestamp descending (recent first)
        assert len(result) == 3
        assert result[0]['metadata']['index'] == 1  # Newest (1 day ago)
        assert result[1]['metadata']['index'] == 2  # Middle (2 days ago)
        assert result[2]['metadata']['index'] == 0  # Oldest (3 days ago)
    
    def test_tie_break_combined_criteria(self):
        """Test tie-break with combined criteria (score > source > timestamp)."""
        # Mixed scores with some ties
        mixed_scores = [0.9, 0.8, 0.8, 0.7, 0.7]
        
        mixed_metadata = [
            {
                'source': 'kg',
                'timestamp': self.now - timedelta(days=1),
                'index': 0
            },
            {
                'source': 'temporal',
                'timestamp': self.now - timedelta(days=1),
                'index': 1
            },
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=2),
                'index': 2
            },
            {
                'source': 'hybrid',
                'timestamp': self.now - timedelta(days=3),
                'index': 3
            },
            {
                'source': 'kg',
                'timestamp': self.now - timedelta(days=1),
                'index': 4
            }
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            mixed_scores, [], [], mixed_metadata
        )
        
        # Expected order:
        # 1. 0.9 (kg, index 0) - highest score
        # 2. 0.8 (hybrid, index 2) - tie on score, hybrid source priority
        # 3. 0.8 (temporal, index 1) - tie on score, temporal source priority  
        # 4. 0.7 (hybrid, index 3) - tie on score, hybrid source priority
        # 5. 0.7 (kg, index 4) - tie on score, kg source priority
        
        assert len(result) == 5
        assert result[0]['score'] == 0.9
        assert result[1]['score'] == 0.8
        assert result[2]['score'] == 0.8
        assert result[3]['score'] == 0.7
        assert result[4]['score'] == 0.7
        
        # Verify source ordering for tied scores
        assert result[1]['metadata']['source'] == 'hybrid'  # 0.8 tie, hybrid first
        assert result[2]['metadata']['source'] == 'temporal'
        assert result[3]['metadata']['source'] == 'hybrid'  # 0.7 tie, hybrid first
        assert result[4]['metadata']['source'] == 'kg'
    
    def test_tie_break_deterministic_consistency(self):
        """Test that tie-break is deterministic across multiple runs."""
        scores = self.equal_scores
        metadata = self.test_metadata
        
        # Run multiple times
        result1 = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], metadata)
        result2 = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], metadata)
        result3 = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], metadata)
        
        # Should produce identical results
        assert result1 == result2 == result3
        
        # Verify ordering is consistent
        for i in range(len(result1)):
            assert result1[i]['score'] == result2[i]['score'] == result3[i]['score']
            assert result1[i]['metadata']['source'] == result2[i]['metadata']['source'] == result3[i]['metadata']['source']
    
    def test_tie_break_missing_metadata(self):
        """Test tie-break behavior with missing metadata."""
        scores = [0.8, 0.7, 0.6]
        
        # Partial metadata (some items missing)
        partial_metadata = [
            {
                'source': 'hybrid',
                'timestamp': self.now,
                'index': 0
            },
            {},  # Missing metadata
            None  # None metadata
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], partial_metadata)
        
        # Should handle missing metadata gracefully
        assert len(result) == 3
        assert result[0]['score'] == 0.8
        assert result[1]['score'] == 0.7
        assert result[2]['score'] == 0.6
        
        # Items with missing metadata should get default values
        assert result[1]['metadata']['source'] == 'unknown'
        assert result[2]['metadata']['source'] == 'unknown'
    
    def test_tie_break_empty_scores(self):
        """Test tie-break with empty score lists."""
        result = self.temporal_fusion.fuse_with_tiebreak([], [], [], [])
        
        # Should return empty result
        assert result == []
    
    def test_tie_break_single_item(self):
        """Test tie-break with single item."""
        scores = [0.8]
        metadata = [{'source': 'hybrid', 'timestamp': self.now}]
        
        result = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], metadata)
        
        # Should return single item
        assert len(result) == 1
        assert result[0]['score'] == 0.8
        assert result[0]['metadata']['source'] == 'hybrid'
    
    def test_tie_break_future_timestamps(self):
        """Test tie-break with future timestamps."""
        future_time = self.now + timedelta(days=1)
        future_metadata = [
            {
                'source': 'hybrid',
                'timestamp': future_time,
                'index': 0
            },
            {
                'source': 'hybrid',
                'timestamp': self.now,
                'index': 1
            }
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            [0.8, 0.8], [], [], future_metadata
        )
        
        # Future timestamps should come first (more recent)
        assert len(result) == 2
        assert result[0]['metadata']['index'] == 0  # Future timestamp
        assert result[1]['metadata']['index'] == 1  # Current timestamp
    
    def test_tie_break_none_timestamps(self):
        """Test tie-break with None timestamps."""
        none_timestamp_metadata = [
            {
                'source': 'hybrid',
                'timestamp': None,
                'index': 0
            },
            {
                'source': 'hybrid',
                'timestamp': self.now,
                'index': 1
            }
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            [0.8, 0.8], [], [], none_timestamp_metadata
        )
        
        # None timestamps should be treated as oldest
        assert len(result) == 2
        assert result[0]['metadata']['index'] == 1  # Has timestamp
        assert result[1]['metadata']['index'] == 0  # None timestamp
    
    def test_tie_break_custom_source_priorities(self):
        """Test tie-break with custom source priorities."""
        # Modify source priorities for testing
        original_priorities = self.temporal_fusion.source_priorities.copy()
        self.temporal_fusion.source_priorities = {
            'custom_high': 1,
            'custom_low': 10,
            'unknown': 999
        }
        
        custom_metadata = [
            {
                'source': 'custom_low',
                'timestamp': self.now,
                'index': 0
            },
            {
                'source': 'custom_high',
                'timestamp': self.now,
                'index': 1
            }
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(
            [0.8, 0.8], [], [], custom_metadata
        )
        
        # Should respect custom priorities
        assert len(result) == 2
        assert result[0]['metadata']['source'] == 'custom_high'  # Priority 1
        assert result[1]['metadata']['source'] == 'custom_low'   # Priority 10
        
        # Restore original priorities
        self.temporal_fusion.source_priorities = original_priorities
    
    def test_tie_break_mixed_score_sources(self):
        """Test tie-break with mixed score and source combinations."""
        scores = [0.7, 0.9, 0.8, 0.8, 0.7]
        metadata = [
            {'source': 'kg', 'timestamp': self.now, 'index': 0},
            {'source': 'temporal', 'timestamp': self.now, 'index': 1},
            {'source': 'hybrid', 'timestamp': self.now, 'index': 2},
            {'source': 'kg', 'timestamp': self.now, 'index': 3},
            {'source': 'hybrid', 'timestamp': self.now, 'index': 4}
        ]
        
        result = self.temporal_fusion.fuse_with_tiebreak(scores, [], [], metadata)
        
        # Expected order: 0.9 > 0.8(hybrid) > 0.8(kg) > 0.7(hybrid) > 0.7(kg)
        assert len(result) == 5
        assert result[0]['score'] == 0.9  # Highest score
        assert result[1]['score'] == 0.8  # Hybrid priority for tie
        assert result[2]['score'] == 0.8  # KG after hybrid
        assert result[3]['score'] == 0.7  # Hybrid priority for tie
        assert result[4]['score'] == 0.7  # KG after hybrid
