"""Feedback Loop - Continuous quality improvement system.

This module collects feedback on signal quality, analyzes patterns,
and adjusts validation thresholds dynamically for optimal outputs.
"""

import logging
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback."""

    EXPLICIT = "explicit"  # User-provided feedback
    IMPLICIT = "implicit"  # Inferred from usage patterns
    AUTOMATIC = "automatic"  # System-generated feedback


@dataclass
class QualityFeedback:
    """Feedback on signal quality."""

    assessment_id: str
    feedback_type: FeedbackType
    timestamp: datetime

    # Quality ratings (1-5 scale)
    accuracy_rating: int | None = None
    relevance_rating: int | None = None
    clarity_rating: int | None = None
    completeness_rating: int | None = None

    # Feedback text
    positive_aspects: list[str] = field(default_factory=list)
    improvement_areas: list[str] = field(default_factory=list)
    user_comments: str | None = None

    # Context
    hop_id: str | None = None
    stage: str | None = None
    user_id: str | None = None


@dataclass
class QualityTrend:
    """Trend analysis for quality metrics."""

    metric_name: str
    current_value: float
    trend_direction: str  # improving, declining, stable
    trend_strength: float  # 0-1, how strong the trend is
    confidence: float  # Statistical confidence in trend

    # Recent values for calculation
    recent_values: list[float] = field(default_factory=list)
    baseline_value: float | None = None


class AdaptiveThresholds:
    """Dynamically adjusting quality thresholds."""

    def __init__(self, initial_thresholds: dict[str, float]):
        """Initialize adaptive thresholds.

        Args:
            initial_thresholds: Starting threshold values
        """
        self.thresholds = initial_thresholds.copy()
        self.adjustment_history: list[dict[str, Any]] = []
        self.min_thresholds = {"excellent": 0.85, "high": 0.70, "good": 0.55, "marginal": 0.40}
        self.max_thresholds = {"excellent": 0.95, "high": 0.85, "good": 0.70, "marginal": 0.55}

    def adjust_thresholds(
        self,
        quality_scores: list[float],
        acceptance_rate: float,
        target_acceptance: float = 0.75,
    ) -> dict[str, float]:
        """Adjust thresholds based on performance.

        Args:
            quality_scores: Recent quality scores
            acceptance_rate: Current acceptance rate
            target_acceptance: Target acceptance rate

        Returns:
            Updated thresholds
        """
        if not quality_scores:
            return self.thresholds

        # Calculate adjustment factor
        acceptance_gap = target_acceptance - acceptance_rate

        if abs(acceptance_gap) < 0.05:  # Within 5% of target
            return self.thresholds

        # Adjust thresholds proportionally
        adjustment_factor = acceptance_gap * 0.1  # Gradual adjustment

        for level in ["excellent", "high", "good", "marginal"]:
            current = self.thresholds.get(level, 0.5)

            # Apply adjustment
            new_value = current + adjustment_factor

            # Clamp to min/max
            new_value = max(self.min_thresholds[level], min(self.max_thresholds[level], new_value))

            self.thresholds[level] = new_value

        # Record adjustment
        self.adjustment_history.append(
            {
                "timestamp": datetime.now(),
                "acceptance_rate": acceptance_rate,
                "adjustment_factor": adjustment_factor,
                "new_thresholds": self.thresholds.copy(),
            },
        )

        logger.info(
            f"Adjusted thresholds: acceptance_rate={acceptance_rate:.2f}, adjustment={adjustment_factor:.3f}",
        )

        return self.thresholds


class FeedbackLoop:
    """Manages feedback collection and quality improvement."""

    def __init__(self, name: str = "default", history_size: int = 1000):
        """Initialize the feedback loop.

        Args:
            name: Loop name for logging
            history_size: Maximum history to retain
        """
        self.name = name
        self.history_size = history_size

        # Data storage
        self.assessments: deque = deque(maxlen=history_size)
        self.feedback: deque = deque(maxlen=history_size)
        self.quality_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Analysis cache
        self._trends_cache: dict[str, QualityTrend] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes

        # Adaptive thresholds
        self.adaptive_thresholds = AdaptiveThresholds(
            {"excellent": 0.9, "high": 0.75, "good": 0.6, "marginal": 0.4},
        )

        # Thread safety
        self._lock = threading.Lock()

        logger.debug(f"Initialized FeedbackLoop: {name}")

    def record_assessment(self, assessment: SignalAssessment) -> None:
        """Record a signal assessment.

        Args:
            assessment: Assessment to record
        """
        with self._lock:
            self.assessments.append(assessment)

            # Update quality history
            self.quality_history["composite"].append(assessment.composite_score)
            self.quality_history["relevance"].append(assessment.relevance_score)
            self.quality_history["authority"].append(assessment.authority_score)
            self.quality_history["coherence"].append(assessment.coherence_score)
            self.quality_history["specificity"].append(assessment.specificity_score)
            self.quality_history["snr"].append(assessment.signal_to_noise_ratio)
            self.quality_history["accuracy"].append(assessment.factual_accuracy)

            # Invalidate cache
            self._cache_timestamp = 0

    def add_feedback(self, feedback: QualityFeedback) -> None:
        """Add feedback to the loop.

        Args:
            feedback: Feedback to add
        """
        with self._lock:
            self.feedback.append(feedback)

            # Link feedback to assessment if possible
            for assessment in reversed(self.assessments):
                if assessment.content_hash == feedback.assessment_id:
                    # Store feedback with assessment
                    assessment.feedback = feedback
                    break

            logger.debug(f"Added {feedback.feedback_type.value} feedback")

    def analyze_trends(self, force_refresh: bool = False) -> dict[str, QualityTrend]:
        """Analyze quality trends.

        Args:
            force_refresh: Force cache refresh

        Returns:
            Dictionary of trends by metric
        """
        now = time.time()

        # Check cache
        if not force_refresh and now - self._cache_timestamp < self._cache_ttl:
            return self._trends_cache

        with self._lock:
            trends = {}

            for metric, values in self.quality_history.items():
                if len(values) < 10:  # Need minimum data
                    continue

                trend = self._calculate_trend(metric, list(values))
                trends[metric] = trend

            # Update cache
            self._trends_cache = trends
            self._cache_timestamp = now

            return trends

    def _calculate_trend(self, metric_name: str, values: list[float]) -> QualityTrend:
        """Calculate trend for a metric.

        Args:
            metric_name: Name of metric
            values: Recent values

        Returns:
            QualityTrend analysis
        """
        if len(values) < 2:
            return QualityTrend(
                metric_name=metric_name,
                current_value=values[0] if values else 0.0,
                trend_direction="stable",
                trend_strength=0.0,
                confidence=0.0,
            )

        # Calculate trend using linear regression
        n = len(values)
        x = list(range(n))

        # Simple linear regression
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Determine trend direction
        if abs(slope) < 0.001:
            direction = "stable"
        elif slope > 0:
            direction = "improving"
        else:
            direction = "declining"

        # Calculate trend strength (normalized slope)
        value_range = max(values) - min(values)
        if value_range > 0:
            strength = min(1.0, abs(slope * n) / value_range)
        else:
            strength = 0.0

        # Calculate confidence based on variance
        variance = statistics.variance(values) if len(values) > 1 else 0
        confidence = max(0.0, 1.0 - (variance / (value_range + 0.001)))

        return QualityTrend(
            metric_name=metric_name,
            current_value=values[-1],
            trend_direction=direction,
            trend_strength=strength,
            confidence=confidence,
            recent_values=values[-10:],  # Last 10 values
            baseline_value=statistics.mean(values[:10]) if len(values) >= 10 else None,
        )

    def get_quality_insights(self) -> dict[str, Any]:
        """Get insights about quality patterns.

        Returns:
            Insights dictionary
        """
        with self._lock:
            if not self.assessments:
                return {"message": "No assessments available"}

            # Calculate statistics
            recent_assessments = list(self.assessments)[-50:]  # Last 50

            # Quality distribution
            quality_counts = defaultdict(int)
            for assessment in recent_assessments:
                quality_counts[assessment.quality_level.value] += 1

            # Common flags
            flag_counts = defaultdict(int)
            for assessment in recent_assessments:
                for flag in assessment.flags:
                    flag_counts[flag] += 1

            # Average scores
            avg_scores = {
                "composite": statistics.mean([a.composite_score for a in recent_assessments]),
                "relevance": statistics.mean([a.relevance_score for a in recent_assessments]),
                "authority": statistics.mean([a.authority_score for a in recent_assessments]),
                "coherence": statistics.mean([a.coherence_score for a in recent_assessments]),
                "specificity": statistics.mean([a.specificity_score for a in recent_assessments]),
            }

            # Hallucination risk analysis
            high_risk_count = sum(1 for a in recent_assessments if a.hallucination_risk > 0.3)

            return {
                "total_assessments": len(self.assessments),
                "recent_assessments": len(recent_assessments),
                "quality_distribution": dict(quality_counts),
                "common_flags": dict(flag_counts),
                "average_scores": avg_scores,
                "high_hallucination_risk_rate": high_risk_count / len(recent_assessments),
                "current_thresholds": self.adaptive_thresholds.thresholds,
                "trends": self.analyze_trends(),
            }

    def recommend_improvements(self) -> list[str]:
        """Recommend improvements based on feedback.

        Returns:
            List of recommendations
        """
        insights = self.get_quality_insights()
        recommendations = []

        # Check quality distribution
        if "quality_distribution" in insights:
            dist = insights["quality_distribution"]
            total = sum(dist.values())

            if total > 0:
                poor_rate = dist.get("poor", 0) / total
                marginal_rate = dist.get("marginal", 0) / total

                if poor_rate > 0.2:
                    recommendations.append(
                        "High rate of poor quality outputs (>20%). "
                        "Consider strengthening input validation and prompt engineering.",
                    )

                if marginal_rate > 0.3:
                    recommendations.append(
                        "Many outputs are only marginal quality. "
                        "Review factual accuracy requirements and add more specific guidelines.",
                    )

        # Check common flags
        if "common_flags" in insights:
            flags = insights["common_flags"]

            if flags.get("LOW_QUALITY", 0) > 5:
                recommendations.append(
                    "Frequent LOW_QUALITY flags detected. "
                    "Increase minimum quality thresholds or enhance training data.",
                )

            if flags.get("HALLUCINATION_RISK", 0) > 3:
                recommendations.append(
                    "Hallucination risks detected. Add stronger fact-checking and source verification.",
                )

            if flags.get("HIGHLY_REPETITIVE", 0) > 5:
                recommendations.append(
                    "High repetition in outputs. Implement diversity constraints and content variety checks.",
                )

        # Check trends
        if "trends" in insights:
            trends = insights["trends"]

            for metric, trend in trends.items():
                if trend.trend_direction == "declining" and trend.confidence > 0.7:
                    recommendations.append(
                        f"{metric.title()} quality is declining with high confidence. "
                        f"Review recent changes and consider targeted improvements.",
                    )

        # Check hallucination risk
        if insights.get("high_hallucination_risk_rate", 0) > 0.15:
            recommendations.append(
                "High hallucination risk rate (>15%). "
                "Implement stricter source verification and reduce speculative language.",
            )

        return recommendations

    def adjust_thresholds_automatically(self) -> dict[str, float]:
        """Automatically adjust thresholds based on performance.

        Returns:
            Updated thresholds
        """
        with self._lock:
            if len(self.assessments) < 20:
                logger.warning("Insufficient data for automatic threshold adjustment")
                return self.adaptive_thresholds.thresholds

            # Calculate acceptance rate
            recent = list(self.assessments)[-20:]
            accepted = sum(
                1
                for a in recent
                if a.quality_level in [SignalQuality.GOOD, SignalQuality.HIGH, SignalQuality.EXCELLENT]
            )
            acceptance_rate = accepted / len(recent)

            # Get quality scores
            quality_scores = [a.composite_score for a in recent]

            # Adjust thresholds
            new_thresholds = self.adaptive_thresholds.adjust_thresholds(
                quality_scores,
                acceptance_rate,
            )

            return new_thresholds

    def export_feedback_data(self) -> dict[str, Any]:
        """Export feedback data for analysis.

        Returns:
            Export data dictionary
        """
        with self._lock:
            return {
                "assessments": [
                    {
                        "content_hash": a.content_hash,
                        "quality_level": a.quality_level.value,
                        "composite_score": a.composite_score,
                        "timestamp": a.timestamp.isoformat(),
                        "flags": a.flags,
                    }
                    for a in self.assessments
                ],
                "feedback": [
                    {
                        "assessment_id": f.assessment_id,
                        "type": f.feedback_type.value,
                        "ratings": {
                            "accuracy": f.accuracy_rating,
                            "relevance": f.relevance_rating,
                            "clarity": f.clarity_rating,
                            "completeness": f.completeness_rating,
                        },
                        "comments": f.user_comments,
                        "timestamp": f.timestamp.isoformat(),
                    }
                    for f in self.feedback
                ],
                "threshold_history": self.adaptive_thresholds.adjustment_history,
                "insights": self.get_quality_insights(),
                "recommendations": self.recommend_improvements(),
            }


# Global feedback loop registry
_feedback_loops: dict[str, FeedbackLoop] = {}
_loop_lock = threading.Lock()


def get_feedback_loop(name: str = "default", history_size: int = 1000) -> FeedbackLoop:
    """Get or create a feedback loop.

    Args:
        name: Loop name
        history_size: Maximum history to retain

    Returns:
        FeedbackLoop instance
    """
    with _loop_lock:
        if name not in _feedback_loops:
            _feedback_loops[name] = FeedbackLoop(name, history_size)
        return _feedback_loops[name]
