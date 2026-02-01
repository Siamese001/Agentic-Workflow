"""
Phase 4 Optimization Tests - Math Operations
Tests for native Python mathematical utilities.
"""

import pytest
from apps_shared.utils.math_operations import MathProcessor, ScoreResult


class TestScoreResult:
    """Test ScoreResult dataclass."""

    def test_score_result_creation(self):
        """Test creating ScoreResult."""
        result = ScoreResult(
            score=0.85,
            normalized_score=0.85,
            breakdown={"component1": 0.9, "component2": 0.8},
            metadata={"total_weight": 2.0},
        )

        assert result.score == 0.85
        assert result.normalized_score == 0.85
        assert len(result.breakdown) == 2


class TestMathProcessor:
    """Test MathProcessor functionality."""

    def test_calculate_percentage_normal(self):
        """Test calculating percentage."""
        result = MathProcessor.calculate_percentage(25, 100)

        assert result == 25.0

    def test_calculate_percentage_zero_total(self):
        """Test calculating percentage with zero total."""
        result = MathProcessor.calculate_percentage(10, 0)

        assert result == 0.0

    def test_calculate_percentage_decimals(self):
        """Test calculating percentage with custom decimals."""
        result = MathProcessor.calculate_percentage(1, 3, decimals=4)

        assert result == 33.3333

    def test_calculate_ratio_normal(self):
        """Test calculating ratio."""
        result = MathProcessor.calculate_ratio(10, 5)

        assert result == 2.0

    def test_calculate_ratio_zero_denominator(self):
        """Test calculating ratio with zero denominator."""
        result = MathProcessor.calculate_ratio(10, 0)

        assert result == 0.0

    def test_normalize_score_to_0_1(self):
        """Test normalizing score to 0-1 range."""
        result = MathProcessor.normalize_score(50, min_val=0, max_val=100)

        assert result == 0.5

    def test_normalize_score_custom_range(self):
        """Test normalizing to custom range."""
        result = MathProcessor.normalize_score(
            50, min_val=0, max_val=100, target_min=0, target_max=10
        )

        assert result == 5.0

    def test_normalize_score_same_min_max(self):
        """Test normalizing with same min and max."""
        result = MathProcessor.normalize_score(50, min_val=50, max_val=50)

        assert result == 0.0

    def test_weighted_average_equal_weights(self):
        """Test weighted average with equal weights."""
        result = MathProcessor.weighted_average([10, 20, 30])

        assert result == 20.0

    def test_weighted_average_custom_weights(self):
        """Test weighted average with custom weights."""
        result = MathProcessor.weighted_average([10, 20, 30], [1, 2, 3])

        assert result == pytest.approx(23.333, rel=0.01)

    def test_weighted_average_empty_values(self):
        """Test weighted average with empty values."""
        result = MathProcessor.weighted_average([])

        assert result == 0.0

    def test_weighted_average_mismatched_lengths(self):
        """Test weighted average with mismatched lengths."""
        with pytest.raises(ValueError):
            MathProcessor.weighted_average([10, 20], [1, 2, 3])

    def test_calculate_statistics_normal(self):
        """Test calculating statistics."""
        result = MathProcessor.calculate_statistics([10, 20, 30, 40, 50])

        assert result["count"] == 5
        assert result["sum"] == 150
        assert result["mean"] == 30
        assert result["median"] == 30
        assert result["min"] == 10
        assert result["max"] == 50
        assert result["stdev"] > 0

    def test_calculate_statistics_empty(self):
        """Test calculating statistics with empty list."""
        result = MathProcessor.calculate_statistics([])

        assert result["count"] == 0
        assert result["mean"] == 0.0

    def test_calculate_statistics_single_value(self):
        """Test calculating statistics with single value."""
        result = MathProcessor.calculate_statistics([42])

        assert result["count"] == 1
        assert result["mean"] == 42
        assert result["stdev"] == 0.0

    def test_clamp_within_range(self):
        """Test clamping value within range."""
        result = MathProcessor.clamp(50, 0, 100)

        assert result == 50

    def test_clamp_below_min(self):
        """Test clamping value below minimum."""
        result = MathProcessor.clamp(-10, 0, 100)

        assert result == 0

    def test_clamp_above_max(self):
        """Test clamping value above maximum."""
        result = MathProcessor.clamp(150, 0, 100)

        assert result == 100

    def test_calculate_similarity_cosine_identical(self):
        """Test cosine similarity with identical vectors."""
        result = MathProcessor.calculate_similarity([1, 2, 3], [1, 2, 3], method="cosine")

        assert result == pytest.approx(1.0, rel=0.01)

    def test_calculate_similarity_cosine_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        result = MathProcessor.calculate_similarity([1, 0], [0, 1], method="cosine")

        assert result == pytest.approx(0.0, abs=0.01)

    def test_calculate_similarity_euclidean(self):
        """Test Euclidean similarity."""
        result = MathProcessor.calculate_similarity([1, 2, 3], [1, 2, 3], method="euclidean")

        assert result == pytest.approx(1.0, rel=0.01)

    def test_calculate_similarity_mismatched_lengths(self):
        """Test similarity with mismatched lengths."""
        with pytest.raises(ValueError):
            MathProcessor.calculate_similarity([1, 2], [1, 2, 3])

    def test_calculate_similarity_unknown_method(self):
        """Test similarity with unknown method."""
        with pytest.raises(ValueError):
            MathProcessor.calculate_similarity([1, 2], [1, 2], method="unknown")

    def test_calculate_growth_rate_positive(self):
        """Test calculating positive growth rate."""
        result = MathProcessor.calculate_growth_rate(100, 150)

        assert result == 50.0

    def test_calculate_growth_rate_negative(self):
        """Test calculating negative growth rate."""
        result = MathProcessor.calculate_growth_rate(100, 75)

        assert result == -25.0

    def test_calculate_growth_rate_zero_old_value(self):
        """Test growth rate with zero old value."""
        result = MathProcessor.calculate_growth_rate(0, 100)

        assert result == 100.0

    def test_moving_average_simple(self):
        """Test calculating moving average."""
        result = MathProcessor.moving_average([1, 2, 3, 4, 5], window_size=3)

        assert len(result) == 3
        assert result[0] == 2.0
        assert result[1] == 3.0
        assert result[2] == 4.0

    def test_moving_average_window_too_large(self):
        """Test moving average with window larger than data."""
        result = MathProcessor.moving_average([1, 2, 3], window_size=5)

        assert result == []

    def test_calculate_score_with_breakdown_equal_weights(self):
        """Test score calculation with equal weights."""
        components = {"comp1": 0.8, "comp2": 0.9, "comp3": 0.7}
        result = MathProcessor.calculate_score_with_breakdown(components)

        assert result.score == pytest.approx(0.8, rel=0.01)
        assert result.breakdown == components

    def test_calculate_score_with_breakdown_custom_weights(self):
        """Test score calculation with custom weights."""
        components = {"comp1": 0.8, "comp2": 0.9}
        weights = {"comp1": 2.0, "comp2": 1.0}
        result = MathProcessor.calculate_score_with_breakdown(components, weights)

        assert result.score == pytest.approx(0.833, rel=0.01)
        assert result.metadata["total_weight"] == 3.0

    def test_calculate_score_with_breakdown_empty(self):
        """Test score calculation with empty components."""
        result = MathProcessor.calculate_score_with_breakdown({})

        assert result.score == 0.0
        assert result.normalized_score == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
