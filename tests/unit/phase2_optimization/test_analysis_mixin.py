"""
Phase 2 Optimization Tests - Analysis Mixin
Tests for shared analysis workflow patterns.
"""

import pytest
from apps_shared.mixins.analysis_mixin import AnalysisMixin, AnalysisResult


class MockAgent(AnalysisMixin):
    """Mock agent for testing AnalysisMixin."""

    pass


class TestAnalysisResult:
    """Test AnalysisResult dataclass."""

    def test_analysis_result_creation(self):
        """Test creating AnalysisResult."""
        result = AnalysisResult(
            summary="Test summary",
            metrics={"metric1": 10},
            insights=["insight1"],
            recommendations=["rec1"],
            confidence=0.95,
        )

        assert result.summary == "Test summary"
        assert result.metrics == {"metric1": 10}
        assert len(result.insights) == 1
        assert len(result.recommendations) == 1
        assert result.confidence == 0.95


class TestAnalysisMixin:
    """Test AnalysisMixin functionality."""

    def test_analyze_metrics_numeric(self):
        """Test analyzing numeric metrics."""
        agent = MockAgent()
        data = [{"score": 10}, {"score": 20}, {"score": 30}]

        result = agent.analyze_metrics(data, ["score"])

        assert "score" in result
        assert result["score"]["count"] == 3
        assert result["score"]["mean"] == 20
        assert result["score"]["median"] == 20
        assert result["score"]["min"] == 10
        assert result["score"]["max"] == 30

    def test_analyze_metrics_categorical(self):
        """Test analyzing categorical metrics."""
        agent = MockAgent()
        data = [{"status": "pass"}, {"status": "pass"}, {"status": "fail"}]

        result = agent.analyze_metrics(data, ["status"])

        assert "status" in result
        assert result["status"]["count"] == 3
        assert result["status"]["unique"] == 2

    def test_analyze_metrics_missing_data(self):
        """Test analyzing metrics with missing data."""
        agent = MockAgent()
        data = [{"score": 10}, {"other": 20}]

        result = agent.analyze_metrics(data, ["score"])

        assert "score" in result
        assert result["score"]["count"] == 1

    def test_analyze_metrics_no_data(self):
        """Test analyzing metrics with no data."""
        agent = MockAgent()
        data = [{"other": 10}]

        result = agent.analyze_metrics(data, ["score"])

        assert "score" in result
        assert "error" in result["score"]

    def test_calculate_trends_increasing(self):
        """Test trend calculation for increasing data."""
        agent = MockAgent()
        time_series = [(1, 10.0), (2, 20.0), (3, 30.0), (4, 40.0), (5, 50.0)]

        result = agent.calculate_trends(time_series, window_size=3)

        assert result["direction"] == "increasing"
        assert result["current_value"] == 50.0
        assert result["rate_of_change"] > 0

    def test_calculate_trends_decreasing(self):
        """Test trend calculation for decreasing data."""
        agent = MockAgent()
        time_series = [(1, 50.0), (2, 40.0), (3, 30.0), (4, 20.0), (5, 10.0)]

        result = agent.calculate_trends(time_series, window_size=3)

        assert result["direction"] == "decreasing"
        assert result["rate_of_change"] < 0

    def test_calculate_trends_insufficient_data(self):
        """Test trend calculation with insufficient data."""
        agent = MockAgent()
        time_series = [(1, 10.0)]

        result = agent.calculate_trends(time_series)

        assert result["trend"] == "insufficient_data"
        assert result["direction"] == "unknown"

    def test_compare_datasets_with_key(self):
        """Test dataset comparison with key."""
        agent = MockAgent()
        dataset_a = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
        dataset_b = [{"id": 2, "name": "b"}, {"id": 3, "name": "c"}]

        result = agent.compare_datasets(dataset_a, dataset_b, comparison_key="id")

        assert result["size_a"] == 2
        assert result["size_b"] == 2
        assert 1 in result["unique_to_a"]
        assert 3 in result["unique_to_b"]
        assert 2 in result["common"]

    def test_compare_datasets_direct(self):
        """Test direct dataset comparison."""
        agent = MockAgent()
        dataset_a = [1, 2, 3, 4]
        dataset_b = [3, 4, 5, 6]

        result = agent.compare_datasets(dataset_a, dataset_b)

        assert 1 in result["unique_to_a"]
        assert 2 in result["unique_to_a"]
        assert 5 in result["unique_to_b"]
        assert 6 in result["unique_to_b"]
        assert 3 in result["common"]
        assert 4 in result["common"]

    def test_generate_insights_threshold_violation(self):
        """Test insight generation with threshold violations."""
        agent = MockAgent()
        analysis_data = {"metric1": {"mean": 100, "stdev": 50}}
        thresholds = {"metric1_mean": 80, "metric1_stdev": 30}

        insights = agent.generate_insights(analysis_data, thresholds)

        assert len(insights) >= 1
        assert any("mean" in insight and "100" in insight for insight in insights)

    def test_generate_insights_no_violations(self):
        """Test insight generation without violations."""
        agent = MockAgent()
        analysis_data = {"metric1": {"mean": 50, "stdev": 10}}
        thresholds = {"metric1_mean": 80, "metric1_stdev": 30}

        insights = agent.generate_insights(analysis_data, thresholds)

        assert len(insights) == 0

    def test_calculate_score_equal_weights(self):
        """Test score calculation with equal weights."""
        agent = MockAgent()
        metrics = {"metric1": 0.8, "metric2": 0.6, "metric3": 1.0}

        score = agent.calculate_score(metrics)

        assert 0.0 <= score <= 1.0
        assert abs(score - 0.8) < 0.01  # (0.8 + 0.6 + 1.0) / 3

    def test_calculate_score_custom_weights(self):
        """Test score calculation with custom weights."""
        agent = MockAgent()
        metrics = {"metric1": 0.8, "metric2": 0.6}
        weights = {"metric1": 2.0, "metric2": 1.0}

        score = agent.calculate_score(metrics, weights)

        assert 0.0 <= score <= 1.0
        # (0.8 * 2.0 + 0.6 * 1.0) / (2.0 + 1.0) = 2.2 / 3.0 = 0.733...
        assert abs(score - 0.733) < 0.01

    def test_calculate_score_empty_metrics(self):
        """Test score calculation with empty metrics."""
        agent = MockAgent()
        metrics = {}

        score = agent.calculate_score(metrics)

        assert score == 0.0

    def test_identify_outliers_with_outliers(self):
        """Test outlier identification with outliers present."""
        agent = MockAgent()
        values = [10.0, 10.0, 10.0, 10.0, 1000.0]  # 1000 is extreme outlier

        result = agent.identify_outliers(values, threshold=1.5)  # Lower threshold

        assert result["outlier_count"] >= 1
        assert any(outlier["value"] == 1000.0 for outlier in result["outliers"])

    def test_identify_outliers_no_outliers(self):
        """Test outlier identification without outliers."""
        agent = MockAgent()
        values = [10.0, 11.0, 12.0, 13.0, 14.0]

        result = agent.identify_outliers(values, threshold=2.0)

        assert result["outlier_count"] == 0

    def test_identify_outliers_insufficient_data(self):
        """Test outlier identification with insufficient data."""
        agent = MockAgent()
        values = [10.0]

        result = agent.identify_outliers(values)

        assert result["outlier_count"] == 0
        assert len(result["outliers"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
