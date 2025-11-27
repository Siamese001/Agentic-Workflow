"""
Tests for temporal scoring functionality - Phase 6 L4 expansion.

Tests recency weighting, weight clamping, normalization, and hop distance effects.
"""

import pytest
from datetime import datetime, timedelta, UTC
from l4.temporal_kg import TemporalKG, TemporalFact, TemporalNodeMetadata


class TestTemporalScoring:
    """Test suite for temporal scoring implementation."""
    
    def setup_method(self):
        """Set up test fixtures for temporal scoring validation."""
        # Create mock pinecone adapter for testing
        class MockPineconeAdapter:
            def upsert_text_records(self, texts, namespace, ids, metadata_list):
                pass
            
            def query_by_text(self, query_text, namespace, top_k, filter_dict=None):
                return []
            
            def delete_records(self, ids, namespace):
                pass
        
        self.mock_adapter = MockPineconeAdapter()
        self.temporal_kg = TemporalKG(self.mock_adapter)
        self.now = datetime.now(UTC)
    
    def test_recency_weighting_0_to_30_days(self):
        """Test that facts 0-30 days old get weight 1.0."""
        # Test various ages within 0-30 days
        test_cases = [
            timedelta(days=0),    # Today
            timedelta(days=7),    # 1 week ago
            timedelta(days=15),   # 2 weeks ago
            timedelta(days=30),   # Exactly 30 days ago
        ]
        
        for age in test_cases:
            timestamp = self.now - age
            weight = self.temporal_kg.compute_temporal_weight(timestamp)
            assert weight == 1.0, f"Expected weight 1.0 for age {age.days}, got {weight}"
    
    def test_recency_weighting_30_to_90_days(self):
        """Test that facts 30-90 days old get weight 0.6."""
        test_cases = [
            timedelta(days=31),   # Just over 30 days
            timedelta(days=45),   # 1.5 months ago
            timedelta(days=60),   # 2 months ago
            timedelta(days=90),   # Exactly 90 days ago
        ]
        
        for age in test_cases:
            timestamp = self.now - age
            weight = self.temporal_kg.compute_temporal_weight(timestamp)
            assert weight == 0.6, f"Expected weight 0.6 for age {age.days}, got {weight}"
    
    def test_recency_weighting_90_to_180_days(self):
        """Test that facts 90-180 days old get weight 0.2."""
        test_cases = [
            timedelta(days=91),   # Just over 90 days
            timedelta(days=120),  # 4 months ago
            timedelta(days=150),  # 5 months ago
            timedelta(days=180),  # Exactly 180 days ago
        ]
        
        for age in test_cases:
            timestamp = self.now - age
            weight = self.temporal_kg.compute_temporal_weight(timestamp)
            assert weight == 0.2, f"Expected weight 0.2 for age {age.days}, got {weight}"
    
    def test_recency_weighting_over_180_days(self):
        """Test that facts over 180 days old get weight 0.05."""
        test_cases = [
            timedelta(days=181),  # Just over 180 days
            timedelta(days=365),  # 1 year ago
            timedelta(days=730),  # 2 years ago
        ]
        
        for age in test_cases:
            timestamp = self.now - age
            weight = self.temporal_kg.compute_temporal_weight(timestamp)
            assert weight == 0.05, f"Expected weight 0.05 for age {age.days}, got {weight}"
    
    def test_weight_clamping_and_normalization(self):
        """Test that weights are properly clamped and normalized."""
        # Test edge cases
        future_timestamp = self.now + timedelta(days=1)
        weight = self.temporal_kg.compute_temporal_weight(future_timestamp)
        assert weight == 1.0, "Future timestamps should get maximum weight"
        
        # Test very old timestamps
        ancient_timestamp = self.now - timedelta(days=3650)  # 10 years ago
        weight = self.temporal_kg.compute_temporal_weight(ancient_timestamp)
        assert weight == 0.05, "Very old timestamps should get minimum weight"
    
    def test_hop_distance_effect_on_weight(self):
        """Test that hop distance affects temporal weight."""
        base_timestamp = self.now - timedelta(days=15)  # Recent: weight 1.0
        
        # Test hop distance multipliers
        test_cases = [
            (0, 1.0),   # No hop penalty
            (1, 0.8),   # 1 hop penalty
            (2, 0.6),   # 2 hop penalty
            (3, 0.4),   # 3 hop penalty
        ]
        
        for hop_distance, expected_multiplier in test_cases:
            metadata = TemporalNodeMetadata(
                timestamp=base_timestamp,
                source="test",
                weight=1.0,
                hop_distance=hop_distance
            )
            
            adjusted_weight = self.temporal_kg.apply_hop_distance_penalty(
                metadata.weight, hop_distance
            )
            expected_weight = 1.0 * expected_multiplier
            assert adjusted_weight == expected_weight, \
                f"Expected weight {expected_weight} for hop {hop_distance}, got {adjusted_weight}"
    
    def test_temporal_node_metadata_creation(self):
        """Test TemporalNodeMetadata dataclass creation and validation."""
        timestamp = self.now - timedelta(days=45)
        metadata = TemporalNodeMetadata(
            timestamp=timestamp,
            source="company_research",
            weight=0.6,
            hop_distance=1
        )
        
        assert metadata.timestamp == timestamp
        assert metadata.source == "company_research"
        assert metadata.weight == 0.6
        assert metadata.hop_distance == 1
    
    def test_temporal_weight_computation_with_metadata(self):
        """Test temporal weight computation using TemporalNodeMetadata."""
        timestamp = self.now - timedelta(days=60)  # Should get weight 0.6 (30-90 day range)
        metadata = TemporalNodeMetadata(
            timestamp=timestamp,
            source="test",
            weight=0.0,  # Will be computed
            hop_distance=0
        )
        
        computed_weight = self.temporal_kg.compute_temporal_weight(timestamp)
        metadata.weight = computed_weight
        
        assert metadata.weight == 0.6
        assert metadata.hop_distance == 0
    
    def test_temporal_scoring_integration_with_facts(self):
        """Test temporal scoring integration with TemporalFact objects."""
        # Create facts with different ages
        recent_fact = TemporalFact(
            id="recent_1",
            subject="company_1",
            predicate="launched_product",
            object="product_a",
            timestamp=self.now - timedelta(days=10),
            source="news"
        )
        
        old_fact = TemporalFact(
            id="old_1",
            subject="company_1",
            predicate="launched_product", 
            object="product_b",
            timestamp=self.now - timedelta(days=200),
            source="news"
        )
        
        recent_weight = self.temporal_kg.compute_temporal_weight(recent_fact.timestamp)
        old_weight = self.temporal_kg.compute_temporal_weight(old_fact.timestamp)
        
        assert recent_weight == 1.0
        assert old_weight == 0.05
        assert recent_weight > old_weight
    
    def test_temporal_scoring_deterministic(self):
        """Test that temporal scoring is deterministic for same inputs."""
        timestamp = self.now - timedelta(days=45)
        
        # Multiple calls should return same result
        weight1 = self.temporal_kg.compute_temporal_weight(timestamp)
        weight2 = self.temporal_kg.compute_temporal_weight(timestamp)
        weight3 = self.temporal_kg.compute_temporal_weight(timestamp)
        
        assert weight1 == weight2 == weight3 == 0.6
