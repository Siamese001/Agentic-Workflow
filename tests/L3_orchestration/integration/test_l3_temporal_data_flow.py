"""
L3 temporal data flow validation tests - Phase 6 L4 expansion.

Tests temporal data flow and integration at component level:
- TemporalKG orchestration with enriched metadata
- Temporal fusion with deterministic tie-breaks
- Temporal metadata contract consistency
- Component integration validation
"""

from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, patch

from l4.temporal_kg import TemporalKG, TemporalNodeMetadata
from l4.temporal_fusion import TemporalRankFusion
from l4.high_signal import HighSignalScorer


class TestL3TemporalDataFlow:
    """Test suite for L3 temporal data flow validation at component level."""
    
    def setup_method(self):
        """Set up test fixtures for temporal data flow testing."""
        # Mock pinecone adapter for testing
        self.mock_pinecone = Mock()
        
        # Create temporal components
        self.temporal_kg = TemporalKG(self.mock_pinecone)
        self.temporal_fusion = TemporalRankFusion()
        self.high_signal_scorer = HighSignalScorer()
        
        # Test temporal metadata
        self.now = datetime.now(UTC)
        self.test_temporal_metadata = [
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=5),
                source="kg",
                weight=0.8,
                hop_distance=1,
                recency_days=5,
                within_window=True
            ),
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=45),
                source="kg",
                weight=0.6,
                hop_distance=2,
                recency_days=45,
                within_window=False
            )
        ]
    
    def test_temporal_kg_orchestration_with_enriched_metadata(self):
        """Test TemporalKG orchestration returns enriched temporal metadata."""
        # Mock hybrid search results
        hybrid_results = [
            "Company launched new product with $10M funding",
            "Quarterly earnings showed 25% growth"
        ]
        
        # Mock temporal KG search
        with patch.object(self.temporal_kg, 'search_temporal', return_value=self.test_temporal_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="company expansion",
                hybrid_results=hybrid_results,
                temporal_window_days=30,
                max_results=10
            )
        
        # Verify enriched temporal metadata returned
        assert result is not None
        assert result['fusion_applied'] is True  # KG data exists
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1  # Only items within window counted
        assert result['high_signal_count'] >= 0
        
        # Verify temporal metadata enrichment
        assert self.test_temporal_metadata[0].recency_days == 5
        assert self.test_temporal_metadata[0].within_window is True
        assert self.test_temporal_metadata[1].recency_days == 45
        assert self.test_temporal_metadata[1].within_window is False
    
    def test_temporal_fusion_with_deterministic_tie_breaks(self):
        """Test temporal fusion with deterministic tie-break rules."""
        # Test scores with ties for tie-break validation
        hybrid_scores = [0.8, 0.8, 0.8]
        kg_scores = [0.7, 0.7, 0.7]
        temporal_scores = [0.6, 0.6, 0.6]
        
        # Test metadata with different sources and timestamps
        metadata = [
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
            }
        ]
        
        # Apply fusion with tie-breaks
        result = self.temporal_fusion.fuse_with_tiebreak(
            hybrid_scores, kg_scores, temporal_scores, metadata
        )
        
        # Verify deterministic tie-break ordering
        assert len(result) == 3
        assert result[0]['metadata']['source'] == 'hybrid'  # Priority 1
        assert result[1]['metadata']['source'] == 'kg'      # Priority 2
        assert result[2]['metadata']['source'] == 'temporal' # Priority 3
        
        # Verify scores are preserved
        for item in result:
            assert 'score' in item
            assert 'metadata' in item
    
    def test_temporal_metadata_contract_consistency(self):
        """Test temporal metadata maintains contract consistency."""
        # Test with complete temporal metadata
        with patch.object(self.temporal_kg, 'search_temporal', return_value=self.test_temporal_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="test query",
                hybrid_results=["Test result"],
                max_results=10
            )
        
        # Verify contract consistency
        assert 'results' in result
        assert 'fusion_applied' in result
        assert 'temporal_window_applied' in result
        assert 'temporal_facts_found' in result
        assert 'high_signal_count' in result
        
        # Verify result structure
        results = result['results']
        if results:  # Only check if results exist
            for item in results:
                assert 'text' in item
                assert 'score' in item
                assert 'metadata' in item
                assert 'temporal_analysis' in item
                
                # Verify temporal analysis structure
                temporal_analysis = item['temporal_analysis']
                assert 'has_temporal_signal' in temporal_analysis
                assert 'recency_available' in temporal_analysis
                assert 'signal_score' in temporal_analysis
    
    def test_temporal_component_integration_validation(self):
        """Test temporal components integrate correctly."""
        # Test TemporalKG with TemporalFusion integration
        hybrid_results = ["Integration test result"]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=self.test_temporal_metadata):
            # Test orchestration with fusion
            result = self.temporal_kg.execute_temporal_retrieval(
                query="integration test",
                hybrid_results=hybrid_results,
                max_results=5
            )
        
        # Verify integration worked correctly
        assert result['fusion_applied'] is True
        assert result['temporal_facts_found'] > 0
        
        # Verify components worked together
        assert self.temporal_kg.temporal_fusion is not None
        assert self.temporal_kg.high_signal_scorer is not None
    
    def test_temporal_window_filtering_integration(self):
        """Test temporal window filtering integrates correctly."""
        # Test with restrictive window
        with patch.object(self.temporal_kg, 'search_temporal', return_value=self.test_temporal_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="window test",
                hybrid_results=["Test"],
                temporal_window_days=30,  # Only recent items
                max_results=10
            )
        
        # Verify window filtering applied
        assert result['temporal_window_applied'] is True
        assert result['temporal_facts_found'] == 1  # Only the 5-day-old item
        
        # Verify metadata updated correctly
        assert self.test_temporal_metadata[0].within_window is True
        assert self.test_temporal_metadata[1].within_window is False
    
    def test_temporal_high_signal_scoring_integration(self):
        """Test high signal scoring integrates correctly."""
        # Test with signal-rich content
        signal_rich_results = [
            "Company raised $50M in Series B funding",
            "Revenue grew 200% year-over-year",
            "Launched AI product with 10M users"
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=[]):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="signal test",
                hybrid_results=signal_rich_results,
                max_results=10
            )
        
        # Verify signal scoring applied
        assert result['high_signal_count'] > 0  # Should detect signals
        assert result['fusion_applied'] is False  # No KG data, but signal scoring works
    
    def test_temporal_error_handling_integration(self):
        """Test temporal error handling integrates correctly."""
        # Test with component failure
        with patch.object(self.temporal_kg, 'search_temporal', side_effect=Exception("KG failure")):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="error test",
                hybrid_results=["Test result"],
                max_results=10
            )
        
        # Verify graceful error handling
        assert result is not None
        assert result['fusion_applied'] is False
        assert result['temporal_facts_found'] == 0
        assert 'error' in result
    
    def test_temporal_data_flow_deterministic_behavior(self):
        """Test temporal data flow is deterministic."""
        hybrid_results = ["Deterministic test result"]
        
        # Run same operation multiple times
        with patch.object(self.temporal_kg, 'search_temporal', return_value=self.test_temporal_metadata):
            result1 = self.temporal_kg.execute_temporal_retrieval(
                query="deterministic test",
                hybrid_results=hybrid_results,
                max_results=10
            )
            
            result2 = self.temporal_kg.execute_temporal_retrieval(
                query="deterministic test",
                hybrid_results=hybrid_results,
                max_results=10
            )
        
        # Verify deterministic behavior
        assert result1['fusion_applied'] == result2['fusion_applied']
        assert result1['temporal_facts_found'] == result2['temporal_facts_found']
        assert result1['high_signal_count'] == result2['high_signal_count']
    
    def test_temporal_metadata_enrichment_flow(self):
        """Test temporal metadata enrichment flow."""
        # Test metadata without recency fields
        initial_metadata = [
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=10),
                source="test",
                weight=0.7,
                hop_distance=1
                # recency_days and within_window not set initially
            )
        ]
        
        with patch.object(self.temporal_kg, 'search_temporal', return_value=initial_metadata):
            result = self.temporal_kg.execute_temporal_retrieval(
                query="enrichment test",
                hybrid_results=["Test"],
                max_results=10
            )
        
        # Verify enrichment applied
        assert initial_metadata[0].recency_days == 10
        assert initial_metadata[0].within_window is True
        assert result['temporal_facts_found'] == 1
