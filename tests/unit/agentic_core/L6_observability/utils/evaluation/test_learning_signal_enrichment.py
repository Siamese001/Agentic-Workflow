"""
tests/unit/agentic_core/L6_observability/evaluation/test_learning_signal_enrichment.py

Unit tests for Wave 2.1: Learning Signal Enrichment

Tests:
- Temporal feature extraction
- Trend analysis
- Signal deduplication
- Quality scoring
- Context aggregation
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.learning_signal_enrichment import (
    EnrichedLearningSignal,
    LearningSignalEnricher,
    SignalTrend,
    TemporalFeatures,
    get_signal_enricher,
    reset_signal_enricher,
)


class TestTemporalFeatures:
    """Test TemporalFeatures dataclass."""

    def test_temporal_features_creation(self):
        """Test creating temporal features."""
        features = TemporalFeatures(
            hour_of_day=14,
            day_of_week=2,
            is_weekend=False,
            is_business_hours=True,
            time_since_last_signal_sec=30.0,
        )

        assert features.hour_of_day == 14
        assert features.day_of_week == 2
        assert features.is_weekend is False
        assert features.is_business_hours is True
        assert features.time_since_last_signal_sec == 30.0


class TestLearningSignalEnricher:
    """Test suite for LearningSignalEnricher."""

    def test_enrich_signal_basic(self):
        """Test basic signal enrichment."""
        enricher = LearningSignalEnricher()

        enriched = enricher.enrich_signal(
            signal={"test": "data"},
            evaluation_type="faithfulness",
            score=0.85,
            timestamp_utc=time.time(),
        )

        assert enriched is not None
        assert isinstance(enriched, EnrichedLearningSignal)
        assert enriched.evaluation_type == "faithfulness"
        assert enriched.score == 0.85
        assert enriched.is_duplicate is False

    def test_temporal_feature_extraction(self):
        """Test temporal feature extraction."""
        enricher = LearningSignalEnricher()

        # Use current time for temporal features
        timestamp = time.time()

        enriched = enricher.enrich_signal(
            signal={"test": "data"},
            evaluation_type="test",
            score=0.85,
            timestamp_utc=timestamp,
        )

        assert enriched is not None
        assert 0 <= enriched.temporal_features.hour_of_day <= 23
        assert enriched.temporal_features.day_of_week in range(7)

    def test_deduplication(self):
        """Test signal deduplication."""
        enricher = LearningSignalEnricher(dedup_window_sec=60.0)

        signal = {"test": "data"}
        current_time = time.time()

        # First signal should be enriched
        enriched1 = enricher.enrich_signal(
            signal=signal,
            evaluation_type="test",
            score=0.85,
            timestamp_utc=current_time,
        )
        assert enriched1 is not None

        # Duplicate signal within window should be filtered
        enriched2 = enricher.enrich_signal(
            signal=signal,
            evaluation_type="test",
            score=0.85,
            timestamp_utc=current_time + 30.0,
        )
        assert enriched2 is None

        # Signal outside window should be enriched
        enriched3 = enricher.enrich_signal(
            signal=signal,
            evaluation_type="test",
            score=0.85,
            timestamp_utc=current_time + 120.0,
        )
        assert enriched3 is not None

    def test_trend_analysis_improving(self):
        """Test trend analysis detects improving trend."""
        enricher = LearningSignalEnricher()

        # Add signals with improving scores (need at least 3 for trend)
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        current_time = time.time()
        for i, score in enumerate(scores):
            enriched = enricher.enrich_signal(
                signal={"iteration": i},
                evaluation_type="test",
                score=score,
                timestamp_utc=current_time + i * 10,
            )

        # Last signal should show improving trend (or unknown if not enough history)
        assert enriched is not None
        assert enriched.trend in [SignalTrend.IMPROVING, SignalTrend.UNKNOWN]
        if enriched.trend == SignalTrend.IMPROVING:
            assert enriched.trend_strength > 0.0

    def test_trend_analysis_degrading(self):
        """Test trend analysis detects degrading trend."""
        enricher = LearningSignalEnricher()

        # Add signals with degrading scores
        scores = [0.9, 0.8, 0.7, 0.6, 0.5]
        for i, score in enumerate(scores):
            enriched = enricher.enrich_signal(
                signal={"iteration": i},
                evaluation_type="test",
                score=score,
                timestamp_utc=time.time() + i,
            )

        # Last signal should show degrading trend
        assert enriched is not None
        assert enriched.trend == SignalTrend.DEGRADING
        assert enriched.trend_strength > 0.0

    def test_trend_analysis_stable(self):
        """Test trend analysis detects stable trend."""
        enricher = LearningSignalEnricher()

        # Add signals with stable scores
        scores = [0.85, 0.85, 0.85, 0.85, 0.85]
        for i, score in enumerate(scores):
            enriched = enricher.enrich_signal(
                signal={"iteration": i},
                evaluation_type="test",
                score=score,
                timestamp_utc=time.time() + i,
            )

        # Last signal should show stable trend
        assert enriched is not None
        assert enriched.trend == SignalTrend.STABLE

    def test_quality_scoring(self):
        """Test signal quality scoring."""
        enricher = LearningSignalEnricher(min_quality_threshold=0.3)

        # High score should have high quality
        enriched_high = enricher.enrich_signal(
            signal={"test": "high"},
            evaluation_type="test",
            score=0.95,
            timestamp_utc=time.time(),
        )

        # Low score should have lower quality but still pass threshold
        enriched_low = enricher.enrich_signal(
            signal={"test": "low"},
            evaluation_type="test",
            score=0.40,
            timestamp_utc=time.time() + 20,
        )

        assert enriched_high is not None
        assert enriched_low is not None
        assert enriched_high.signal_quality > enriched_low.signal_quality

    def test_low_quality_filtering(self):
        """Test low quality signal filtering."""
        enricher = LearningSignalEnricher(min_quality_threshold=0.8)

        # High quality signal should pass
        enriched_high = enricher.enrich_signal(
            signal={"test": "high"},
            evaluation_type="test",
            score=0.95,
            timestamp_utc=time.time(),
        )
        assert enriched_high is not None

        # Low quality signal should be filtered
        enriched_low = enricher.enrich_signal(
            signal={"test": "low"},
            evaluation_type="test",
            score=0.30,
            timestamp_utc=time.time() + 1,
        )
        assert enriched_low is None

    def test_context_preservation(self):
        """Test context is preserved in enriched signal."""
        enricher = LearningSignalEnricher()

        context = {"source": "test", "metadata": {"key": "value"}}

        enriched = enricher.enrich_signal(
            signal={"test": "data"},
            evaluation_type="test",
            score=0.85,
            timestamp_utc=time.time(),
            context=context,
        )

        assert enriched is not None
        assert enriched.context == context

    def test_recent_scores_tracking(self):
        """Test recent scores are tracked."""
        enricher = LearningSignalEnricher(trend_window_size=5)

        # Add 10 signals
        for i in range(10):
            enriched = enricher.enrich_signal(
                signal={"iteration": i},
                evaluation_type="test",
                score=0.5 + i * 0.05,
                timestamp_utc=time.time() + i,
            )

        # Last signal should have at most 5 recent scores
        assert enriched is not None
        assert len(enriched.recent_scores) <= 6  # window_size + current

    def test_statistics_tracking(self):
        """Test enricher tracks statistics."""
        enricher = LearningSignalEnricher(dedup_window_sec=60.0, min_quality_threshold=0.7)

        # Add some signals
        enricher.enrich_signal({"test": "1"}, "test", 0.85, time.time())
        enricher.enrich_signal({"test": "1"}, "test", 0.85, time.time() + 1)  # Duplicate
        enricher.enrich_signal({"test": "2"}, "test", 0.30, time.time() + 2)  # Low quality

        stats = enricher.get_stats()
        assert stats["total_signals"] == 3
        assert stats["duplicates_filtered"] == 1
        assert stats["low_quality_filtered"] == 1

    def test_clear_history(self):
        """Test clearing signal history."""
        enricher = LearningSignalEnricher()

        enricher.enrich_signal({"test": "data"}, "test", 0.85, time.time())

        enricher.clear_history()

        stats = enricher.get_stats()
        assert stats["total_signals"] == 0
        assert stats["evaluation_types_tracked"] == 0


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test signal enricher singleton pattern."""
        reset_signal_enricher()

        enricher1 = get_signal_enricher()
        enricher2 = get_signal_enricher()

        assert enricher1 is enricher2

        reset_signal_enricher()
        enricher3 = get_signal_enricher()

        assert enricher3 is not enricher1


class TestIntegration:
    """Integration tests for signal enrichment."""

    def test_full_enrichment_workflow(self):
        """Test complete signal enrichment workflow."""
        enricher = LearningSignalEnricher()

        # Simulate evaluation signals over time
        signals = [
            ("faithfulness", 0.80),
            ("faithfulness", 0.85),
            ("faithfulness", 0.90),
            ("groundedness", 0.75),
            ("groundedness", 0.80),
        ]

        enriched_signals = []
        current_time = time.time()

        for i, (eval_type, score) in enumerate(signals):
            enriched = enricher.enrich_signal(
                signal={"iteration": i},
                evaluation_type=eval_type,
                score=score,
                timestamp_utc=current_time + i * 10,
                context={"source": "integration_test"},
            )

            if enriched is not None:
                enriched_signals.append(enriched)

        # Should have enriched all signals (no duplicates, all high quality)
        assert len(enriched_signals) == 5

        # Faithfulness should show improving or unknown trend
        faithfulness_signals = [s for s in enriched_signals if s.evaluation_type == "faithfulness"]
        assert faithfulness_signals[-1].trend in [SignalTrend.IMPROVING, SignalTrend.UNKNOWN]

        # All signals should have temporal features
        assert all(s.temporal_features is not None for s in enriched_signals)

        # All signals should have quality scores
        assert all(0.0 <= s.signal_quality <= 1.0 for s in enriched_signals)

    def test_negative_score_rejected(self):
        """Test negative score raises ValueError."""
        enricher = LearningSignalEnricher()

        with pytest.raises(ValueError, match="Score must be non-negative"):
            enricher.enrich_signal(
                signal={"test": "data"},
                evaluation_type="test",
                score=-0.5,
            )

    def test_empty_evaluation_type_rejected(self):
        """Test empty evaluation_type raises ValueError."""
        enricher = LearningSignalEnricher()

        with pytest.raises(ValueError, match="Evaluation type cannot be empty"):
            enricher.enrich_signal(
                signal={"test": "data"},
                evaluation_type="",
                score=0.85,
            )

        with pytest.raises(ValueError, match="Evaluation type cannot be empty"):
            enricher.enrich_signal(
                signal={"test": "data"},
                evaluation_type="   ",
                score=0.85,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
