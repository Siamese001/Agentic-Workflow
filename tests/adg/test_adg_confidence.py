"""Test ADG confidence functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgConfidence:
    """Test ADG confidence functionality."""

    def test_adg_confidence_engine_exists(self):
        """Test ADG confidence engine module exists."""
        from system_learning.confidence import engine

        assert engine is not None

    def test_adg_confidence_types_defined(self):
        """Test ADG confidence types are defined."""
        from system_learning.confidence.types import ConfidenceLevel

        # Should have confidence levels
        levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        for level in levels:
            assert hasattr(ConfidenceLevel, level) or level in dir(ConfidenceLevel)

    def test_adg_confidence_has_calculate_function(self):
        """Test ADG confidence has calculate function."""
        from system_learning.confidence.engine import calculate_confidence

        assert callable(calculate_confidence)

    def test_adg_confidence_threshold_constants(self):
        """Test confidence threshold constants exist."""
        from system_learning.confidence.engine import CONFIDENCE_THRESHOLD

        assert isinstance(CONFIDENCE_THRESHOLD, (int, float))
        assert 0 <= CONFIDENCE_THRESHOLD <= 1

    def test_adg_confidence_score_range(self):
        """Test confidence scores are in valid range."""
        from system_learning.confidence.engine import ConfidenceScore

        score = ConfidenceScore(value=0.5, level="MEDIUM")
        assert 0 <= score.value <= 1

    def test_adg_confidence_factors_exist(self):
        """Test confidence factors are defined."""
        from system_learning.confidence.types import ConfidenceFactor

        factors = ["COVERAGE", "COMPLEXITY", "TEST_RESULTS", "STATIC_ANALYSIS"]
        for factor in factors:
            assert hasattr(ConfidenceFactor, factor) or factor in dir(ConfidenceFactor)


if __name__ == '__main__':
    pytest.main()
