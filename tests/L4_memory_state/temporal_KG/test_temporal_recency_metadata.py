"""
Temporal recency metadata tests - Phase 6 L4 expansion.

Tests recency_days and within_window metadata fields:
- Recency calculation accuracy
- Temporal window filtering
- Metadata consistency
- Edge cases for recency calculations
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, patch

from l4.temporal_kg import TemporalKG, TemporalNodeMetadata


class TestTemporalRecencyMetadata:
    """Test suite for temporal recency metadata functionality."""
    
    def setup_method(self):
        """Set up test fixtures for recency metadata testing."""
        self.mock_adapter = Mock()
        self.temporal_kg = TemporalKG(self.mock_adapter)
        self.now = datetime.now(UTC)
    
    def test_recency_days_calculation_recent(self):
        """Test recency_days calculation for recent content."""
        # Create recent metadata (5 days ago)
        recent_timestamp = self.now - timedelta(days=5)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=recent_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=None,
                max_results=10
            )
        
        # Should calculate recency_days correctly
        assert result is not None
        assert result['temporal_facts_found'] == 1
        # The metadata should have recency_days set
        assert mock_metadata[0].recency_days == 5
        assert mock_metadata[0].within_window is True
    
    def test_recency_days_calculation_old(self):
        """Test recency_days calculation for old content."""
        # Create old metadata (100 days ago)
        old_timestamp = self.now - timedelta(days=100)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=old_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=None,
                max_results=10
            )
        
        # Should calculate recency_days correctly
        assert result is not None
        assert result['temporal_facts_found'] == 1
        assert mock_metadata[0].recency_days == 100
        assert mock_metadata[0].within_window is True
    
    def test_temporal_window_within_window(self):
        """Test temporal window filtering for content within window."""
        # Create recent metadata within 30-day window
        recent_timestamp = self.now - timedelta(days=15)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=recent_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=30,
                max_results=10
            )
        
        # Should include content within window
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1
        assert mock_metadata[0].recency_days == 15
        assert mock_metadata[0].within_window is True
    
    def test_temporal_window_outside_window(self):
        """Test temporal window filtering for content outside window."""
        # Create old metadata outside 30-day window
        old_timestamp = self.now - timedelta(days=45)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=old_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=30,
                max_results=10
            )
        
        # Should filter out content outside window
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 0  # Filtered out
        assert mock_metadata[0].recency_days == 45
        assert mock_metadata[0].within_window is False
    
    def test_temporal_window_boundary_conditions(self):
        """Test temporal window filtering at boundary conditions."""
        # Test exactly at boundary (30 days)
        boundary_timestamp = self.now - timedelta(days=30)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=boundary_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=30,
                max_results=10
            )
        
        # Should include content exactly at boundary
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1
        assert mock_metadata[0].recency_days == 30
        assert mock_metadata[0].within_window is True
    
    def test_temporal_window_one_day_outside(self):
        """Test temporal window filtering one day outside boundary."""
        # Test one day outside boundary (31 days)
        outside_timestamp = self.now - timedelta(days=31)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=outside_timestamp,
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=30,
                max_results=10
            )
        
        # Should filter out content one day outside
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 0
        assert mock_metadata[0].recency_days == 31
        assert mock_metadata[0].within_window is False
    
    def test_multiple_items_mixed_recency(self):
        """Test recency metadata with multiple items of mixed ages."""
        # Create metadata with mixed recency
        mixed_metadata = [
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=5),   # Recent
                source="recent",
                weight=0.9,
                hop_distance=1
            ),
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=35),  # Outside window
                source="old",
                weight=0.7,
                hop_distance=2
            ),
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=15),  # Within window
                source="medium",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mixed_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=30,
                max_results=10
            )
        
        # Should filter correctly and maintain metadata
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 2  # Only recent and medium
        
        # Check individual metadata
        assert mixed_metadata[0].recency_days == 5
        assert mixed_metadata[0].within_window is True
        
        assert mixed_metadata[1].recency_days == 35
        assert mixed_metadata[1].within_window is False
        
        assert mixed_metadata[2].recency_days == 15
        assert mixed_metadata[2].within_window is True
    
    def test_recency_metadata_without_window(self):
        """Test recency metadata when no temporal window is specified."""
        # Create metadata without window constraint
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=60),
                source="test",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=None,  # No window constraint
                max_results=10
            )
        
        # Should set recency metadata but mark all as within_window
        assert result is not None
        assert result['temporal_window_applied'] is False
        assert result['temporal_facts_found'] == 1
        assert mock_metadata[0].recency_days == 60
        assert mock_metadata[0].within_window is True  # All marked as within when no window
    
    def test_recency_zero_days_ago(self):
        """Test recency metadata for very recent content (today)."""
        # Create metadata from today
        today_timestamp = self.now
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=today_timestamp,
                source="today",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=7,
                max_results=10
            )
        
        # Should handle zero days ago correctly
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1
        assert mock_metadata[0].recency_days == 0
        assert mock_metadata[0].within_window is True
    
    def test_recency_future_timestamp(self):
        """Test recency metadata handling for future timestamps."""
        # Create metadata with future timestamp (edge case)
        future_timestamp = self.now + timedelta(days=1)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=future_timestamp,
                source="future",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                temporal_window_days=7,
                max_results=10
            )
        
        # Should handle future timestamps gracefully
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1
        # Future timestamp should result in negative recency_days
        assert mock_metadata[0].recency_days <= 0
        assert mock_metadata[0].within_window is True
    
    def test_recency_metadata_consistency(self):
        """Test that recency metadata remains consistent across operations."""
        # Create metadata
        original_timestamp = self.now - timedelta(days=10)
        mock_metadata = [
            TemporalNodeMetadata(
                timestamp=original_timestamp,
                source="consistent",
                weight=0.8,
                hop_distance=1
            )
        ]
        
        # Run multiple operations
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_metadata):
            result1 = self.temporal_kg.execute_temporal_retrieval(
                query="test query 1",
                hybrid_results=["Result 1"],
                temporal_window_days=30,
                max_results=10
            )
            
            result2 = self.temporal_kg.execute_temporal_retrieval(
                query="test query 2", 
                hybrid_results=["Result 2"],
                temporal_window_days=15,
                max_results=5
            )
        
        # Metadata should remain consistent
        assert result1['temporal_facts_found'] == 1
        assert result2['temporal_facts_found'] == 1
        
        # Recency should be calculated the same way
        assert mock_metadata[0].recency_days == 10
        assert mock_metadata[0].within_window is True  # Within both windows
