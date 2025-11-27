"""
Tests for high signal scoring functionality - Phase 6 L4 expansion.

Tests HighSignalScore correctness, signal detection, and rationale generation.
"""

import pytest
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
from l4.temporal_kg import TemporalKG, TemporalNodeMetadata
from l4.high_signal import HighSignalScore, HighSignalScorer


class TestHighSignalScoring:
    """Test suite for high signal scoring implementation."""
    
    def setup_method(self):
        """Set up test fixtures for high signal scoring validation."""
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
        self.scorer = HighSignalScorer()
        self.now = datetime.now(UTC)
    
    def test_high_signal_score_creation(self):
        """Test HighSignalScore dataclass creation and validation."""
        score = HighSignalScore(
            score=0.85,
            rationale="Contains numeric metrics and recent product launch"
        )
        
        assert score.score == 0.85
        assert score.rationale == "Contains numeric metrics and recent product launch"
        assert 0.0 <= score.score <= 1.0
    
    def test_high_signal_score_bounds_validation(self):
        """Test that HighSignalScore enforces 0-1 bounds."""
        # Test valid scores
        valid_scores = [0.0, 0.5, 1.0]
        for score_value in valid_scores:
            score = HighSignalScore(score=score_value, rationale="test")
            assert score.score == score_value
        
        # Test score normalization (should be implemented in scorer)
        # This test will be updated based on actual implementation
    
    def test_numeric_mentions_boost(self):
        """Test that numeric mentions receive appropriate boost."""
        # Test content with various numeric patterns
        test_cases = [
            ("Revenue grew by 25%", "Contains percentage metric"),
            ("Serves 10M customers", "Contains large number with unit"),
            ("Reduced costs by $2.5M", "Contains monetary value"),
            ("Improved efficiency by 3x", "Contains multiplier"),
            ("No numbers here", "No numeric mentions found")
        ]
        
        for content, expected_rationale in test_cases:
            score = self.scorer.compute_signal_score(content)
            assert isinstance(score, HighSignalScore)
            assert score.score >= 0.0
            assert score.score <= 1.0
            
            # Check numeric keywords only for content that should have them
            if content != "No numbers here":
                assert any(keyword in score.rationale.lower() for keyword in ["numeric", "number", "metric"]), \
                    f"Expected numeric keywords in rationale for '{content}', got: '{score.rationale}'"
                assert score.score > 0, f"Expected positive score for numeric content '{content}', got: {score.score}"
            else:
                # The negative case should have no numeric keywords and zero score
                assert not any(keyword in score.rationale.lower() for keyword in ["numeric", "number", "metric"]), \
                    f"Expected no numeric keywords in rationale for '{content}', got: '{score.rationale}'"
                assert score.score == 0, f"Expected zero score for non-numeric content '{content}', got: {score.score}"
    
    def test_product_launches_boost(self):
        """Test that product launch mentions receive appropriate boost."""
        product_launch_keywords = [
            "launched new product",
            "released version 2.0",
            "introduced platform",
            "debuted technology",
            "unveiled solution"
        ]
        
        for keyword in product_launch_keywords:
            content = f"The company {keyword} last quarter"
            score = self.scorer.compute_signal_score(content)
            assert isinstance(score, HighSignalScore)
            assert score.score > 0.5, f"Product launch should boost score: {keyword}"
            assert "launch" in score.rationale.lower() or "product" in score.rationale.lower()
    
    def test_hiring_trends_boost(self):
        """Test that hiring trend mentions receive appropriate boost."""
        hiring_keywords = [
            "hiring 100 engineers",
            "recruiting for AI team",
            "expanding workforce",
            "job openings increased",
            "talent acquisition"
        ]
        
        for keyword in hiring_keywords:
            content = f"The company is {keyword} this year"
            score = self.scorer.compute_signal_score(content)
            assert isinstance(score, HighSignalScore)
            assert score.score > 0.4, f"Hiring trends should boost score: {keyword}"
            assert any(word in score.rationale.lower() for word in ["hiring", "recruit", "workforce"])
    
    def test_strategy_pivots_boost(self):
        """Test that strategy pivot mentions receive appropriate boost."""
        strategy_keywords = [
            "pivoted to AI",
            "strategic shift",
            "changed business model",
            "market repositioning",
            "strategic realignment"
        ]
        
        for keyword in strategy_keywords:
            content = f"The company {keyword} recently"
            score = self.scorer.compute_signal_score(content)
            assert isinstance(score, HighSignalScore)
            assert score.score > 0.6, f"Strategy pivots should boost score: {keyword}"
            assert any(word in score.rationale.lower() for word in ["strategy", "pivot", "shift"])
    
    def test_recency_weight_multiplicative(self):
        """Test that recency weight is applied multiplicatively."""
        # Content with strong signals
        content = "Launched AI product serving 10M customers with $5M revenue"
        
        # Test with different recency weights
        recency_weights = [1.0, 0.6, 0.2, 0.05]
        
        base_score = self.scorer.compute_signal_score(content, recency_weight=1.0)
        
        for recency_weight in recency_weights[1:]:
            adjusted_score = self.scorer.compute_signal_score(content, recency_weight=recency_weight)
            
            # Adjusted score should be lower due to recency penalty
            assert adjusted_score.score <= base_score.score, \
                f"Recency weight {recency_weight} should reduce score"
    
    def test_multiple_signals_combined(self):
        """Test that multiple signal types are combined appropriately."""
        # Content with multiple high-signal indicators
        content = "Launched AI product serving 10M customers, hiring 200 engineers, pivoted to cloud strategy"
        
        score = self.scorer.compute_signal_score(content)
        
        assert isinstance(score, HighSignalScore)
        assert score.score > 0.8, "Multiple signals should result in high score"
        
        # Rationale should mention multiple signal types
        rationale_lower = score.rationale.lower()
        signal_keywords = ["launch", "numeric", "hiring", "strategy"]
        mentioned_signals = sum(1 for keyword in signal_keywords if keyword in rationale_lower)
        assert mentioned_signals >= 2, f"Should mention multiple signals: {score.rationale}"
    
    def test_high_signal_scoring_deterministic(self):
        """Test that high signal scoring is deterministic for same inputs."""
        content = "Launched product with 25% revenue growth"
        
        # Multiple calls should return same result
        score1 = self.scorer.compute_signal_score(content)
        score2 = self.scorer.compute_signal_score(content)
        score3 = self.scorer.compute_signal_score(content)
        
        assert score1.score == score2.score == score3.score
        assert score1.rationale == score2.rationale == score3.rationale
    
    def test_high_signal_scoring_with_temporal_metadata(self):
        """Test high signal scoring using TemporalNodeMetadata."""
        metadata = TemporalNodeMetadata(
            timestamp=self.now - timedelta(days=15),  # Recent: high temporal weight
            source="company_research",
            weight=1.0,
            hop_distance=0
        )
        
        content = "Launched new AI platform serving enterprise customers"
        score = self.scorer.compute_signal_score_with_metadata(content, metadata)
        
        assert isinstance(score, HighSignalScore)
        assert score.score > 0.7, "Recent high-signal content should score very high"
        assert "launch" in score.rationale.lower()
    
    def test_high_signal_scoring_hop_distance_penalty(self):
        """Test that hop distance affects high signal scoring."""
        base_content = "Launched product with $10M revenue"
        
        # Test different hop distances
        hop_distances = [0, 1, 2, 3]
        scores = []
        
        for hop_distance in hop_distances:
            metadata = TemporalNodeMetadata(
                timestamp=self.now - timedelta(days=10),
                source="test",
                weight=1.0,
                hop_distance=hop_distance
            )
            score = self.scorer.compute_signal_score_with_metadata(base_content, metadata)
            scores.append(score.score)
        
        # Scores should decrease with hop distance
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], \
                f"Scores should decrease with hop distance: {scores}"
    
    def test_high_signal_scoring_edge_cases(self):
        """Test high signal scoring with edge cases."""
        edge_cases = [
            ("", "Empty content"),
            ("   ", "Whitespace only"),
            ("No signals here", "No high-signal content"),
            ("123", "Numbers only"),
            ("LAUNCHED!", "Single signal word"),
        ]
        
        for content, description in edge_cases:
            score = self.scorer.compute_signal_score(content)
            assert isinstance(score, HighSignalScore)
            assert 0.0 <= score.score <= 1.0, f"Score should be valid for {description}"
            assert isinstance(score.rationale, str), f"Rationale should be string for {description}"
    
    def test_high_signal_scoring_integration_with_temporal_kg(self):
        """Test high signal scoring integration with temporal KG."""
        # Create temporal facts with high-signal content
        high_signal_fact = {
            "content": "Launched AI platform serving 1M customers, hiring 50 engineers",
            "timestamp": self.now - timedelta(days=20),
            "source": "company_news"
        }
        
        low_signal_fact = {
            "content": "General company information",
            "timestamp": self.now - timedelta(days=200),
            "source": "general_info"
        }
        
        high_score = self.scorer.compute_signal_score(
            high_signal_fact["content"],
            recency_weight=self.temporal_kg.compute_temporal_weight(high_signal_fact["timestamp"])
        )
        
        low_score = self.scorer.compute_signal_score(
            low_signal_fact["content"],
            recency_weight=self.temporal_kg.compute_temporal_weight(low_signal_fact["timestamp"])
        )
        
        assert high_score.score > low_score.score, \
            "High-signal recent content should score higher than low-signal old content"
    
    def test_high_signal_scoring_performance(self):
        """Test that high signal scoring performs efficiently."""
        import time
        
        content = "Launched product with 25% revenue growth, hiring 100 engineers"
        
        # Test performance with multiple calls
        start_time = time.time()
        for _ in range(100):
            self.scorer.compute_signal_score(content)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.01, f"Average scoring time should be < 10ms, got {avg_time:.4f}s"
