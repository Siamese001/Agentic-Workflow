"""
Negative path tests for temporal KG components - Phase 6 L4 expansion.

Tests robustness of temporal components under failure conditions:
- Empty hybrid search results
- Empty KG results  
- Both empty results
- Malformed metadata
- Component failures
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, patch

from l4.temporal_kg import TemporalKG, TemporalNodeMetadata
from l4.temporal_fusion import TemporalRankFusion
from l4.high_signal import HighSignalScorer


class TestTemporalNegativePaths:
    """Test suite for negative path scenarios in temporal components."""
    
    def setup_method(self):
        """Set up test fixtures for negative path testing."""
        # Mock pinecone adapter for testing
        self.mock_adapter = Mock()
        self.temporal_kg = TemporalKG(self.mock_adapter)
        self.temporal_fusion = TemporalRankFusion()
        self.high_signal_scorer = HighSignalScorer()
    
    def test_hybrid_empty_kg_only_path(self):
        """Test hybrid empty → KG-only path with safe fallback."""
        # Empty hybrid results
        hybrid_results = []
        
        # Mock KG search to return some results
        mock_kg_metadata = [
            TemporalNodeMetadata(
                timestamp=datetime.now(UTC),
                source="kg",
                weight=0.8,
                hop_distance=1,
                recency_days=5,
                within_window=True
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_kg_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should return KG-only results
        assert result is not None
        assert result['fusion_applied'] is True  # KG scores available
        assert result['temporal_facts_found'] == 1
        assert result['results'] == []  # No hybrid text to process
        assert 'error' not in result
    
    def test_kg_empty_hybrid_only_path(self):
        """Test KG empty → hybrid-only path with safe fallback."""
        # Non-empty hybrid results
        hybrid_results = ["Result 1", "Result 2"]
        
        # Mock KG search to return empty results
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should return hybrid-only results
        assert result is not None
        assert result['fusion_applied'] is False  # No KG scores
        assert result['temporal_facts_found'] == 0
        assert len(result['results']) == 2
        assert result['results'][0]['text'] == "Result 1"
        assert result['results'][1]['text'] == "Result 2"
        assert 'error' not in result
    
    def test_both_empty_safe_fallback(self):
        """Test both empty → safe fallback stub."""
        # Both hybrid and KG empty
        hybrid_results = []
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should return safe fallback
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert result['high_signal_count'] == 0
        assert result['results'] == []
        assert 'error' not in result
    
    def test_malformed_metadata_safe_fallback(self):
        """Test malformed metadata → safe fallback."""
        # Hybrid results with malformed metadata
        hybrid_results = ["Result 1", "Result 2"]
        
        # Mock KG search to return malformed metadata
        mock_kg_metadata = [
            TemporalNodeMetadata(
                timestamp=None,  # Malformed timestamp
                source="",        # Empty source
                weight=-1.0,     # Invalid weight
                hop_distance=-1,  # Invalid hop distance
                recency_days=None,
                within_window=False
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_kg_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should handle malformed metadata gracefully
        assert result is not None
        assert result['fusion_applied'] is True
        assert result['temporal_facts_found'] == 1
        assert len(result['results']) == 2
        assert 'error' not in result
    
    def test_temporal_kg_component_failure(self):
        """Test temporal KG component failure → safe fallback."""
        hybrid_results = ["Result 1", "Result 2"]
        
        # Mock search_temporal to raise exception
        with patch.object(self.temporal_kg, 'search_temporal', side_effect=Exception("KG failure")):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should handle KG failure gracefully
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert result['high_signal_count'] == 0
        assert result['results'] == []
        assert 'error' in result
        assert result['error'] == "KG failure"
    
    def test_high_signal_scorer_failure(self):
        """Test high signal scorer failure → safe fallback."""
        hybrid_results = ["Result 1", "Result 2"]
        
        # Mock high signal scorer to raise exception
        with patch.object(self.high_signal_scorer, 'compute_signal_score', side_effect=Exception("Signal scoring failure")):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should handle signal scoring failure gracefully
        assert result is not None
        assert result['fusion_applied'] is False  # Falls back to hybrid only
        assert result['temporal_facts_found'] == 0
        assert len(result['results']) == 2
        assert 'error' not in result  # Handled internally
    
    def test_temporal_fusion_failure(self):
        """Test temporal fusion failure → safe fallback."""
        hybrid_results = ["Result 1", "Result 2"]
        
        # Mock temporal fusion to raise exception
        with patch.object(self.temporal_fusion, 'fuse_with_tiebreak', side_effect=Exception("Fusion failure")):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should handle fusion failure gracefully
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert len(result['results']) == 2
        assert 'error' not in result  # Handled internally
    
    def test_temporal_window_filtering_empty(self):
        """Test temporal window filtering with empty results."""
        hybrid_results = []
        temporal_window_days = 30
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                temporal_window_days=temporal_window_days,
                max_results=10
            )
        
        # Should handle empty temporal window gracefully
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 0
        assert result['results'] == []
        assert 'error' not in result
    
    def test_temporal_window_filtering_no_matches(self):
        """Test temporal window filtering with no matches."""
        hybrid_results = ["Result 1"]
        temporal_window_days = 1  # Very restrictive
        
        # Mock KG results outside window
        old_timestamp = datetime.now(UTC).replace(day=1)  # Old date
        mock_kg_metadata = [
            TemporalNodeMetadata(
                timestamp=old_timestamp,
                source="kg",
                weight=0.8,
                hop_distance=1,
                recency_days=365,  # Outside window
                within_window=False
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=mock_kg_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                temporal_window_days=temporal_window_days,
                max_results=10
            )
        
        # Should filter out old results
        assert result is not None
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 0  # Filtered out
        assert len(result['results']) == 1  # Still has hybrid result
        assert 'error' not in result
    
    def test_null_query_handling(self):
        """Test null/empty query handling."""
        hybrid_results = ["Result 1"]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="",  # Empty query
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Should handle empty query gracefully
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert len(result['results']) == 1
        assert 'error' not in result
    
    def test_max_results_zero_handling(self):
        """Test max_results=0 handling."""
        hybrid_results = ["Result 1", "Result 2", "Result 3"]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=hybrid_results,
                max_results=0  # Zero results requested
            )
        
        # Should handle zero max results gracefully
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert len(result['results']) == 0  # No results due to max_results=0
        assert 'error' not in result
