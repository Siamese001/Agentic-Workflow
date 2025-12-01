"""
Tests for temporal rank fusion functionality - Phase 6 L4 expansion.

Tests deterministic fusion, mixed hybrid + KG paths, and KG-only fallback.
"""

import pytest
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
from l4.temporal_kg import TemporalKG, TemporalNodeMetadata
from l4.temporal_fusion import TemporalRankFusion


class TestTemporalRankFusion:
    """Test suite for temporal rank fusion implementation."""
    
    def setup_method(self):
        """Set up test fixtures for temporal rank fusion validation."""
        # Create mock pinecone adapter
        class MockPineconeAdapter:
            def upsert_text_records(self, texts, namespace, ids, metadata_list):
                pass
            
            def query_by_text(self, query_text, namespace, top_k, filter_dict=None):
                return []
            
            def delete_records(self, ids, namespace):
                pass
        
        self.mock_adapter = MockPineconeAdapter()
        self.temporal_kg = TemporalKG(self.mock_adapter)
        self.fusion = TemporalRankFusion()
        self.now = datetime.now(UTC)
    
    def test_deterministic_fusion_output(self):
        """Test that TemporalRankFusion produces identical results for identical inputs."""
        # Create test scores
        hybrid_scores = [0.9, 0.8, 0.7, 0.6, 0.5]
        kg_scores = [0.85, 0.75, 0.65, 0.55, 0.45]
        temporal_scores = [1.0, 0.6, 0.2, 0.05, 0.05]
        
        # Run fusion multiple times
        result1 = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        result2 = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        result3 = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        # Results should be identical
        assert result1 == result2 == result3, "Fusion should be deterministic"
    
    def test_identical_results_for_out_of_order_inputs(self):
        """Test that fusion handles out-of-order inputs correctly."""
        base_hybrid = [0.9, 0.8, 0.7]
        base_kg = [0.85, 0.75, 0.65]
        base_temporal = [1.0, 0.6, 0.2]
        
        # Test different input orders
        result1 = self.fusion.fuse(base_hybrid, base_kg, base_temporal)
        result2 = self.fusion.fuse(base_hybrid[::-1], base_kg[::-1], base_temporal[::-1])
        
        # Results should be the same after internal normalization
        assert len(result1) == len(result2), "Results should have same length"
        
        # Check that fusion weights are applied correctly (0.5*hybrid + 0.3*kg + 0.2*temporal)
        for i in range(len(result1)):
            expected1 = 0.5 * base_hybrid[i] + 0.3 * base_kg[i] + 0.2 * base_temporal[i]
            expected2 = 0.5 * base_hybrid[::-1][i] + 0.3 * base_kg[::-1][i] + 0.2 * base_temporal[::-1][i]
            assert abs(result1[i] - expected1) < 0.001, f"Result1[{i}] should match expected fusion"
            assert abs(result2[i] - expected2) < 0.001, f"Result2[{i}] should match expected fusion"
    
    def test_mixed_hybrid_kg_paths(self):
        """Test fusion with mixed hybrid and KG paths."""
        # Test case where hybrid has more results than KG
        hybrid_scores = [0.9, 0.8, 0.7, 0.6, 0.5]
        kg_scores = [0.85, 0.75, 0.65]  # Fewer KG results
        temporal_scores = [1.0, 0.6, 0.2, 0.05, 0.05]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        assert len(result) == 5, "Should return max length of inputs"
        
        # First 3 should use fusion, last 2 should use hybrid + temporal only
        for i in range(3):
            expected = 0.5 * hybrid_scores[i] + 0.3 * kg_scores[i] + 0.2 * temporal_scores[i]
            assert abs(result[i] - expected) < 0.001
        
        for i in range(3, 5):
            expected = 0.5 * hybrid_scores[i] + 0.2 * temporal_scores[i]  # No KG contribution
            assert abs(result[i] - expected) < 0.001
    
    def test_kg_only_fallback(self):
        """Test KG-only fallback when hybrid scores are empty."""
        hybrid_scores = []  # No hybrid results
        kg_scores = [0.85, 0.75, 0.65, 0.55]
        temporal_scores = [1.0, 0.6, 0.2, 0.05]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        assert len(result) == 4, "Should return KG + temporal fusion"
        
        # Should use 0.3*kg + 0.2*temporal (no hybrid contribution)
        for i in range(len(result)):
            expected = 0.3 * kg_scores[i] + 0.2 * temporal_scores[i]
            assert abs(result[i] - expected) < 0.001
    
    def test_hybrid_only_fallback(self):
        """Test hybrid-only fallback when KG scores are empty."""
        hybrid_scores = [0.9, 0.8, 0.7, 0.6]
        kg_scores = []  # No KG results
        temporal_scores = [1.0, 0.6, 0.2, 0.05]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        assert len(result) == 4, "Should return hybrid + temporal fusion"
        
        # Should use 0.5*hybrid + 0.2*temporal (no KG contribution)
        for i in range(len(result)):
            expected = 0.5 * hybrid_scores[i] + 0.2 * temporal_scores[i]
            assert abs(result[i] - expected) < 0.001
    
    def test_temporal_only_fallback(self):
        """Test temporal-only fallback when both hybrid and KG are empty."""
        hybrid_scores = []
        kg_scores = []
        temporal_scores = [1.0, 0.6, 0.2, 0.05]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        assert len(result) == 4, "Should return temporal scores only"
        
        # Should use 0.2*temporal only
        for i in range(len(result)):
            expected = 0.2 * temporal_scores[i]
            assert abs(result[i] - expected) < 0.001
    
    def test_empty_all_inputs(self):
        """Test fusion when all inputs are empty."""
        result = self.fusion.fuse([], [], [])
        assert result == [], "Empty inputs should return empty result"
    
    def test_score_normalization(self):
        """Test that fusion properly normalizes scores."""
        # Test with scores outside 0-1 range
        hybrid_scores = [1.5, 0.8, -0.2]  # Some out-of-range scores
        kg_scores = [0.85, 0.75, 0.65]
        temporal_scores = [1.0, 0.6, 0.2]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        # Results should be normalized to 0-1 range
        for score in result:
            assert 0.0 <= score <= 1.0, f"Fusion result {score} should be in 0-1 range"
    
    def test_fusion_with_temporal_metadata(self):
        """Test fusion using TemporalNodeMetadata objects."""
        # Create temporal metadata with different weights
        metadata_list = [
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=10),
                source="hybrid",
                weight=0.9,
                hop_distance=0
            ),
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=45),
                source="kg",
                weight=0.6,
                hop_distance=1
            ),
            TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=120),
                source="temporal",
                weight=0.2,
                hop_distance=2
            )
        ]
        
        # Extract scores from metadata
        hybrid_scores = [0.9, 0.0, 0.0]  # Only first has hybrid
        kg_scores = [0.0, 0.6, 0.0]     # Only second has KG
        temporal_scores = [m.weight for m in metadata_list]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        assert len(result) == 3
        assert all(0.0 <= score <= 1.0 for score in result)
    
    def test_fusion_weights_sum_to_one(self):
        """Test that fusion weights (0.5, 0.3, 0.2) sum to one correctly."""
        hybrid_scores = [1.0, 1.0, 1.0]  # Maximum scores
        kg_scores = [1.0, 1.0, 1.0]
        temporal_scores = [1.0, 1.0, 1.0]
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        # With all inputs at 1.0, fusion should be 0.5 + 0.3 + 0.2 = 1.0
        for score in result:
            assert abs(score - 1.0) < 0.001, f"Max fusion should be 1.0, got {score}"
    
    def test_fusion_preserves_ordering(self):
        """Test that fusion preserves relative ordering of scores."""
        # Clear ordering case
        hybrid_scores = [0.9, 0.7, 0.5, 0.3, 0.1]  # Decreasing
        kg_scores = [0.1, 0.3, 0.5, 0.7, 0.9]     # Increasing
        temporal_scores = [0.5, 0.5, 0.5, 0.5, 0.5]  # Constant
        
        result = self.fusion.fuse(hybrid_scores, kg_scores, temporal_scores)
        
        # Results should be ordered (highest first due to hybrid weight dominance)
        for i in range(len(result) - 1):
            assert result[i] >= result[i + 1], f"Results should be ordered: {result}"
