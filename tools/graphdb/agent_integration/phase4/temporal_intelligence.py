"""Temporal Intelligence - Time-series architectural analysis and forecasting.

This module provides temporal intelligence capabilities that enable
analysis of architectural evolution over time and predictive forecasting.
"""

from __future__ import annotations

import logging
import time
import math
from tqdm import tqdm
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase3.ecosystem_intelligence import EcosystemIntelligenceEngine

logger = logging.getLogger(__name__)


class TemporalPattern(Enum):
    """Types of temporal patterns."""

    SEASONAL = "seasonal"
    TREND = "trend"
    CYCLICAL = "cyclical"
    IRREGULAR = "irregular"
    BURST = "burst"
    DECAY = "decay"


class CausalityType(Enum):
    """Types of causal relationships."""

    DIRECT = "direct"
    INDIRECT = "indirect"
    CORRELATIONAL = "correlational"
    SPURIOUS = "spurious"
    FEEDBACK = "feedback"


@dataclass
class TemporalPoint:
    """Represents a point in time with architectural state."""

    timestamp: datetime
    metrics: Dict[str, float]
    events: List[str]
    context_snapshot: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class TemporalPattern:
    """Represents a temporal pattern in architectural evolution."""

    pattern_id: str
    pattern_type: TemporalPattern
    start_time: datetime
    end_time: datetime
    duration: timedelta
    strength: float  # 0.0 to 1.0
    periodicity: Optional[timedelta]
    description: str
    supporting_points: List[TemporalPoint]


@dataclass
class CausalRelationship:
    """Represents a causal relationship between architectural events."""

    relationship_id: str
    cause_event: str
    effect_event: str
    causality_type: CausalityType
    strength: float  # 0.0 to 1.0
    time_lag: timedelta
    confidence: float
    evidence: List[TemporalPoint]


@dataclass
class TemporalForecast:
    """Represents a temporal forecast of architectural evolution."""

    forecast_id: str
    forecast_horizon: timedelta
    predictions: List[Dict[str, Any]]
    confidence_intervals: Dict[str, Tuple[float, float]]
    model_accuracy: float
    generated_at: datetime


class TemporalIntelligenceEngine:
    """Temporal intelligence engine for time-series architectural analysis."""

    def __init__(self, ecosystem_engine: EcosystemIntelligenceEngine):
        """Initialize temporal intelligence engine.

        Args:
            ecosystem_engine: Ecosystem intelligence engine for context
        """
        self.ecosystem_engine = ecosystem_engine

        # Temporal data storage
        self.temporal_data: deque[TemporalPoint] = deque(maxlen=10000)
        self.temporal_patterns: Dict[str, TemporalPattern] = {}
        self.causal_relationships: Dict[str, CausalRelationship] = {}

        # Temporal configuration
        self.temporal_config = {
            "max_history_days": 365,
            "pattern_detection_threshold": 0.7,
            "causality_threshold": 0.6,
            "forecast_horizon_days": 30,
            "time_granularity": "hour",  # minute, hour, day, week
        }

        # Time series models
        self.forecasting_models = {
            "linear_regression": self._linear_regression_forecast,
            "exponential_smoothing": self._exponential_smoothing_forecast,
            "arima": self._arima_forecast,
            "lstm": self._lstm_forecast,
            "prophet": self._prophet_forecast,
        }

        logger.info("TemporalIntelligenceEngine initialized")

    def record_temporal_state(
        self, context: ArchitecturalContext, metrics: Optional[Dict[str, float]] = None
    ) -> TemporalPoint:
        """Record current architectural state in temporal database.

        Args:
            context: Current architectural context
            metrics: Optional metrics to record

        Returns:
            TemporalPoint representing the recorded state
        """
        # Calculate default metrics if not provided
        if metrics is None:
            metrics = self._calculate_default_metrics(context)

        # Create temporal point
        temporal_point = TemporalPoint(
            timestamp=datetime.now(),
            metrics=metrics,
            events=[context.action_type],
            context_snapshot={
                "agent_type": context.agent_type,
                "action_type": context.action_type,
                "target_modules": context.target_modules,
                "session_id": context.session_id,
            },
            confidence=0.9,
        )

        # Store temporal point
        self.temporal_data.append(temporal_point)

        logger.debug("Recorded temporal state with %d metrics", len(metrics))

        return temporal_point

    def analyze_temporal_patterns(self, time_window: Optional[int] = None) -> Dict[str, TemporalPattern]:
        """Analyze temporal patterns in architectural evolution.

        Args:
            time_window: Time window in days (None for all available data)

        Returns:
            Dictionary of detected temporal patterns
        """
        logger.info("Analyzing temporal patterns")

        # Filter data by time window
        filtered_data = self._filter_temporal_data(time_window)

        if len(filtered_data) < 10:
            logger.warning("Insufficient temporal data for pattern analysis")
            return {}

        # Detect different types of patterns
        patterns = {}

        # Detect seasonal patterns
        seasonal_patterns = self._detect_seasonal_patterns(filtered_data)
        patterns.update(seasonal_patterns)

        # Detect trend patterns
        trend_patterns = self._detect_trend_patterns(filtered_data)
        patterns.update(trend_patterns)

        # Detect cyclical patterns
        cyclical_patterns = self._detect_cyclical_patterns(filtered_data)
        patterns.update(cyclical_patterns)

        # Detect burst patterns
        burst_patterns = self._detect_burst_patterns(filtered_data)
        patterns.update(burst_patterns)

        # Update pattern registry
        self.temporal_patterns.update(patterns)

        logger.info("Detected %d temporal patterns", len(patterns))

        return patterns

    def analyze_causality(
        self, cause_event: str, effect_event: str, time_window: Optional[int] = None
    ) -> Optional[CausalRelationship]:
        """Analyze causal relationship between events.

        Args:
            cause_event: Event that may cause the effect
            effect_event: Event that may be caused by the cause
            time_window: Time window in days for analysis

        Returns:
            CausalRelationship if detected, None otherwise
        """
        logger.info("Analyzing causality between %s and %s", cause_event, effect_event)

        # Filter data by time window
        filtered_data = self._filter_temporal_data(time_window)

        # Find occurrences of cause and effect events
        cause_occurrences = []
        effect_occurrences = []

        for point in tqdm(filtered_data, desc="causality scan", unit="point", leave=False):
            if cause_event in point.events:
                cause_occurrences.append(point)
            if effect_event in point.events:
                effect_occurrences.append(point)

        if not cause_occurrences or not effect_occurrences:
            logger.info("Insufficient occurrences for causality analysis")
            return None

        # Calculate causal metrics
        causality_strength = self._calculate_causality_strength(cause_occurrences, effect_occurrences)

        if causality_strength < self.temporal_config["causality_threshold"]:
            logger.info("Causality strength below threshold: %.3f", causality_strength)
            return None

        # Determine time lag
        time_lag = self._calculate_time_lag(cause_occurrences, effect_occurrences)

        # Determine causality type
        causality_type = self._determine_causality_type(cause_occurrences, effect_occurrences, time_lag)

        # Create causal relationship
        relationship = CausalRelationship(
            relationship_id=f"causal_{cause_event}_{effect_event}_{int(time.time())}",
            cause_event=cause_event,
            effect_event=effect_event,
            causality_type=causality_type,
            strength=causality_strength,
            time_lag=time_lag,
            confidence=min(0.9, causality_strength + 0.1),
            evidence=cause_occurrences[:5],  # Top 5 supporting points
        )

        # Store relationship
        self.causal_relationships[relationship.relationship_id] = relationship

        logger.info(
            "Found causal relationship: %s -> %s (strength: %.3f)",
            cause_event,
            effect_event,
            causality_strength,
        )

        return relationship

    def forecast_architectural_evolution(
        self, context: ArchitecturalContext, forecast_horizon_days: int = 30, model: str = "linear_regression"
    ) -> TemporalForecast:
        """Forecast architectural evolution over time.

        Args:
            context: Current architectural context
            forecast_horizon_days: Number of days to forecast
            model: Forecasting model to use

        Returns:
            TemporalForecast with predictions
        """
        logger.info("Forecasting architectural evolution for %d days using %s", forecast_horizon_days, model)

        # Get historical data for forecasting
        historical_data = list(self.temporal_data)

        if len(historical_data) < 5:
            logger.warning("Insufficient historical data for forecasting")
            return self._create_default_forecast(forecast_horizon_days)

        # Prepare time series data
        time_series_data = self._prepare_time_series_data(historical_data, context)

        # Generate forecast
        forecast_func = self.forecasting_models.get(model)
        if not forecast_func:
            logger.warning("Unknown forecasting model: %s, using default", model)
            forecast_func = self._linear_regression_forecast

        predictions = forecast_func(time_series_data, forecast_horizon_days)

        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(time_series_data, predictions)

        # Calculate model accuracy
        model_accuracy = self._calculate_model_accuracy(time_series_data, predictions)

        forecast = TemporalForecast(
            forecast_id=f"forecast_{context.session_id}_{int(time.time())}",
            forecast_horizon=timedelta(days=forecast_horizon_days),
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            model_accuracy=model_accuracy,
            generated_at=datetime.now(),
        )

        logger.info("Forecast generated with accuracy %.3f", model_accuracy)

        return forecast

    def detect_anomalies(
        self, context: ArchitecturalContext, sensitivity: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in temporal patterns.

        Args:
            context: Current architectural context
            sensitivity: Sensitivity threshold for anomaly detection

        Returns:
            List of detected anomalies
        """
        logger.info("Detecting temporal anomalies with sensitivity %.2f", sensitivity)

        anomalies = []

        # Get recent temporal data
        recent_data = list(self.temporal_data)[-50:]  # Last 50 points

        if len(recent_data) < 10:
            logger.warning("Insufficient data for anomaly detection")
            return anomalies

        # Calculate statistical baselines
        baselines = self._calculate_statistical_baselines(recent_data)

        # Check current state against baselines
        current_metrics = self._calculate_default_metrics(context)

        for metric_name, current_value in tqdm(current_metrics.items(), desc="baseline check", unit="metric", leave=False):
            if metric_name in baselines:
                baseline = baselines[metric_name]

                # Calculate z-score
                if baseline["std"] > 0:
                    z_score = abs(current_value - baseline["mean"]) / baseline["std"]

                    if z_score > (3.0 * (2.0 - sensitivity)):  # Adjust threshold based on sensitivity
                        anomaly = {
                            "type": "statistical_anomaly",
                            "metric": metric_name,
                            "current_value": current_value,
                            "baseline_mean": baseline["mean"],
                            "z_score": z_score,
                            "severity": "high" if z_score > 4 else "medium",
                            "timestamp": datetime.now().isoformat(),
                        }
                        anomalies.append(anomaly)

        # Check for pattern anomalies
        pattern_anomalies = self._detect_pattern_anomalies(recent_data, sensitivity)
        anomalies.extend(pattern_anomalies)

        logger.info("Detected %d temporal anomalies", len(anomalies))

        return anomalies

    def get_temporal_summary(self, time_window_days: int = 7) -> Dict[str, Any]:
        """Get summary of temporal intelligence over time window.

        Args:
            time_window_days: Time window in days

        Returns:
            Temporal summary statistics
        """
        # Filter data by time window
        filtered_data = self._filter_temporal_data(time_window_days)

        if not filtered_data:
            return {"error": "No temporal data available"}

        # Calculate summary statistics
        summary = {
            "time_window_days": time_window_days,
            "data_points": len(filtered_data),
            "time_range": {
                "start": filtered_data[0].timestamp.isoformat(),
                "end": filtered_data[-1].timestamp.isoformat(),
            },
            "metrics_summary": {},
            "events_summary": {},
            "patterns_detected": len(
                [
                    p
                    for p in self.temporal_patterns.values()
                    if p.start_time >= datetime.now() - timedelta(days=time_window_days)
                ]
            ),
            "causal_relationships": len(
                [r for r in self.causal_relationships.values() if r.confidence > 0.7]
            ),
        }

        # Calculate metrics summary
        all_metrics = defaultdict(list)
        for point in filtered_data:
            for metric_name, value in point.metrics.items():
                all_metrics[metric_name].append(value)

        for metric_name, values in all_metrics.items():
            if values:
                summary["metrics_summary"][metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "trend": self._calculate_simple_trend(values),
                }

        # Calculate events summary
        event_counts = defaultdict(int)
        for point in filtered_data:
            for event in point.events:
                event_counts[event] += 1

        summary["events_summary"] = dict(event_counts)

        return summary

    def _calculate_default_metrics(self, context: ArchitecturalContext) -> Dict[str, float]:
        """Calculate default metrics for architectural context."""
        metrics = {
            "complexity_score": min(len(context.target_modules) / 10.0, 1.0),
            "activity_level": 0.8,  # Mock activity level
            "risk_score": 0.3,  # Mock risk score
            "performance_score": 0.7,  # Mock performance score
            "dependency_count": len(context.target_modules),
            "change_magnitude": 0.5,  # Mock change magnitude
        }

        return metrics

    def _filter_temporal_data(self, time_window: Optional[int]) -> List[TemporalPoint]:
        """Filter temporal data by time window."""
        if not time_window:
            return list(self.temporal_data)

        cutoff_time = datetime.now() - timedelta(days=time_window)
        return [point for point in self.temporal_data if point.timestamp >= cutoff_time]

    def _detect_seasonal_patterns(self, data: List[TemporalPoint]) -> Dict[str, TemporalPattern]:
        """Detect seasonal patterns in temporal data."""
        patterns = {}

        # Group data by hour of day, day of week, etc.
        hourly_patterns = defaultdict(list)
        daily_patterns = defaultdict(list)
        weekly_patterns = defaultdict(list)

        for point in data:
            hourly_patterns[point.timestamp.hour].append(point)
            daily_patterns[point.timestamp.day].append(point)
            weekly_patterns[point.timestamp.weekday()].append(point)

        # Check for significant seasonal patterns
        for period, grouped_data in tqdm([
            ("hourly", hourly_patterns),
            ("daily", daily_patterns),
            ("weekly", weekly_patterns),
        ], desc="seasonal periods", unit="period", leave=False):
            for key, points in tqdm(grouped_data.items(), desc=f"  {period} groups", unit="group", leave=False):
                if len(points) >= 5:  # Minimum points for pattern detection
                    # Calculate pattern strength
                    strength = self._calculate_pattern_strength(points)

                    if strength > self.temporal_config["pattern_detection_threshold"]:
                        pattern = TemporalPattern(
                            pattern_id=f"seasonal_{period}_{key}_{int(time.time())}",
                            pattern_type=TemporalPattern.SEASONAL,
                            start_time=min(p.timestamp for p in points),
                            end_time=max(p.timestamp for p in points),
                            duration=max(p.timestamp for p in points) - min(p.timestamp for p in points),
                            strength=strength,
                            periodicity=timedelta(hours=1)
                            if period == "hourly"
                            else timedelta(days=1)
                            if period == "daily"
                            else timedelta(weeks=1),
                            description=f"Seasonal pattern detected for {period} {key}",
                            supporting_points=points,
                        )
                        patterns[pattern.pattern_id] = pattern

        return patterns

    def _detect_trend_patterns(self, data: List[TemporalPoint]) -> Dict[str, TemporalPattern]:
        """Detect trend patterns in temporal data."""
        patterns = {}

        # Analyze trends for each metric
        for metric_name in tqdm(["complexity_score", "activity_level", "risk_score"], desc="trend analysis", unit="metric", leave=False):
            values = [point.metrics.get(metric_name, 0.0) for point in data if metric_name in point.metrics]

            if len(values) >= 10:
                # Calculate trend
                trend = self._calculate_simple_trend(values)

                if abs(trend) > 0.1:  # Significant trend
                    pattern = TemporalPattern(
                        pattern_id=f"trend_{metric_name}_{int(time.time())}",
                        pattern_type=TemporalPattern.TREND,
                        start_time=data[0].timestamp,
                        end_time=data[-1].timestamp,
                        duration=data[-1].timestamp - data[0].timestamp,
                        strength=abs(trend),
                        periodicity=None,
                        description=f"{'Increasing' if trend > 0 else 'Decreasing'} trend in {metric_name}",
                        supporting_points=data,
                    )
                    patterns[pattern.pattern_id] = pattern

        return patterns

    def _detect_cyclical_patterns(self, data: List[TemporalPoint]) -> Dict[str, TemporalPattern]:
        """Detect cyclical patterns in temporal data."""
        patterns = {}

        # Simple cyclical pattern detection using autocorrelation
        for metric_name in tqdm(["activity_level", "performance_score"], desc="cyclical analysis", unit="metric", leave=False):
            values = [point.metrics.get(metric_name, 0.0) for point in data if metric_name in point.metrics]

            if len(values) >= 20:
                # Calculate autocorrelation for different lags
                max_correlation = 0.0
                best_lag = 0

                for lag in range(1, min(len(values) // 4, 24)):  # Check lags up to 24 hours/days
                    correlation = self._calculate_autocorrelation(values, lag)
                    if abs(correlation) > max_correlation:
                        max_correlation = abs(correlation)
                        best_lag = lag

                if max_correlation > 0.5:  # Significant cyclical pattern
                    pattern = TemporalPattern(
                        pattern_id=f"cyclical_{metric_name}_{int(time.time())}",
                        pattern_type=TemporalPattern.CYCLICAL,
                        start_time=data[0].timestamp,
                        end_time=data[-1].timestamp,
                        duration=data[-1].timestamp - data[0].timestamp,
                        strength=max_correlation,
                        periodicity=timedelta(hours=best_lag),
                        description=f"Cyclical pattern in {metric_name} with period {best_lag}",
                        supporting_points=data,
                    )
                    patterns[pattern.pattern_id] = pattern

        return patterns

    def _detect_burst_patterns(self, data: List[TemporalPoint]) -> Dict[str, TemporalPattern]:
        """Detect burst patterns in temporal data."""
        patterns = {}

        # Look for sudden spikes in activity
        activity_values = [point.metrics.get("activity_level", 0.0) for point in data]

        if len(activity_values) >= 10:
            # Calculate moving average and standard deviation
            window_size = min(5, len(activity_values) // 3)

            for i in tqdm(range(window_size, len(activity_values)), desc="anomaly window", unit="step", leave=False):
                window_values = activity_values[i - window_size : i]
                current_value = activity_values[i]

                mean_val = np.mean(window_values)
                std_val = np.std(window_values)

                # Check for burst (value > mean + 2*std)
                if std_val > 0 and current_value > mean_val + 2 * std_val:
                    pattern = TemporalPattern(
                        pattern_id=f"burst_activity_{i}_{int(time.time())}",
                        pattern_type=TemporalPattern.BURST,
                        start_time=data[i].timestamp,
                        end_time=data[i].timestamp,
                        duration=timedelta(minutes=5),  # Short duration for burst
                        strength=min((current_value - mean_val) / std_val / 2.0, 1.0),
                        periodicity=None,
                        description=f"Activity burst detected at index {i}",
                        supporting_points=[data[i]],
                    )
                    patterns[pattern.pattern_id] = pattern

        return patterns

    def _calculate_pattern_strength(self, points: List[TemporalPoint]) -> float:
        """Calculate strength of a pattern."""
        if len(points) < 2:
            return 0.0

        # Calculate consistency of metrics across points
        metric_variances = []

        for metric_name in ["complexity_score", "activity_level"]:
            values = [point.metrics.get(metric_name, 0.0) for point in points if metric_name in point.metrics]

            if len(values) >= 2:
                variance = np.var(values)
                metric_variances.append(variance)

        # Pattern strength is inversely related to variance
        if metric_variances:
            avg_variance = np.mean(metric_variances)
            strength = max(0.0, 1.0 - avg_variance)
        else:
            strength = 0.5

        return strength

    def _calculate_simple_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend."""
        if len(values) < 2:
            return 0.0

        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)

        # Calculate slope
        n = len(values)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        return slope

    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at given lag."""
        if len(values) <= lag:
            return 0.0

        n = len(values) - lag
        x = values[:-lag]
        y = values[lag:]

        # Calculate correlation
        mean_x = np.mean(x)
        mean_y = np.mean(y)

        numerator = np.sum((x - mean_x) * (y - mean_y))
        denominator = np.sqrt(np.sum((x - mean_x) ** 2) * np.sum((y - mean_y) ** 2))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_causality_strength(
        self, cause_occurrences: List[TemporalPoint], effect_occurrences: List[TemporalPoint]
    ) -> float:
        """Calculate strength of causal relationship."""
        # Simplified Granger causality approximation
        cause_times = [point.timestamp for point in cause_occurrences]
        effect_times = [point.timestamp for point in effect_occurrences]

        # Count how often effect follows cause within reasonable time window
        time_window = timedelta(hours=1)  # 1 hour window
        follow_count = 0

        for cause_time in cause_times:
            for effect_time in effect_times:
                if cause_time < effect_time <= cause_time + time_window:
                    follow_count += 1
                    break

        # Calculate causality strength
        if len(cause_occurrences) > 0:
            causality_strength = follow_count / len(cause_occurrences)
        else:
            causality_strength = 0.0

        return causality_strength

    def _calculate_time_lag(
        self, cause_occurrences: List[TemporalPoint], effect_occurrences: List[TemporalPoint]
    ) -> timedelta:
        """Calculate typical time lag between cause and effect."""
        time_lags = []
        time_window = timedelta(hours=24)  # 24 hour window

        for cause_point in cause_occurrences:
            for effect_point in effect_occurrences:
                if cause_point.timestamp < effect_point.timestamp <= cause_point.timestamp + time_window:
                    lag = effect_point.timestamp - cause_point.timestamp
                    time_lags.append(lag)

        if time_lags:
            # Return median time lag
            sorted_lags = sorted(time_lags)
            median_lag = sorted_lags[len(sorted_lags) // 2]
            return median_lag

        return timedelta(hours=1)  # Default lag

    def _determine_causality_type(
        self,
        cause_occurrences: List[TemporalPoint],
        effect_occurrences: List[TemporalPoint],
        time_lag: timedelta,
    ) -> CausalityType:
        """Determine type of causal relationship."""
        # Simplified causality type determination
        if time_lag < timedelta(minutes=5):
            return CausalityType.DIRECT
        elif time_lag < timedelta(hours=1):
            return CausalityType.INDIRECT
        elif time_lag < timedelta(hours=6):
            return CausalityType.CORRELATIONAL
        else:
            return CausalityType.SPURIOUS

    def _prepare_time_series_data(
        self, historical_data: List[TemporalPoint], context: ArchitecturalContext
    ) -> Dict[str, List[float]]:
        """Prepare time series data for forecasting."""
        time_series = {}

        # Extract time series for each metric
        for metric_name in ["complexity_score", "activity_level", "risk_score"]:
            values = []
            for point in historical_data:
                if metric_name in point.metrics:
                    values.append(point.metrics[metric_name])

            if values:
                time_series[metric_name] = values

        return time_series

    def _linear_regression_forecast(
        self, time_series: Dict[str, List[float]], forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast using linear regression."""
        predictions = []

        for day in tqdm(range(1, forecast_horizon_days + 1), desc="linear forecast", unit="day", leave=False):
            prediction = {"timestamp": (datetime.now() + timedelta(days=day)).isoformat(), "metrics": {}}

            for metric_name, values in tqdm(time_series.items(), desc="  metrics", unit="metric", leave=False):
                if len(values) >= 2:
                    # Simple linear extrapolation
                    trend = self._calculate_simple_trend(values)
                    last_value = values[-1]
                    predicted_value = last_value + trend * day

                    # Ensure value is in reasonable range
                    predicted_value = max(0.0, min(1.0, predicted_value))
                    prediction["metrics"][metric_name] = predicted_value
                else:
                    prediction["metrics"][metric_name] = 0.5  # Default value

            predictions.append(prediction)

        return predictions

    def _exponential_smoothing_forecast(
        self, time_series: Dict[str, List[float]], forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast using exponential smoothing."""
        predictions = []

        for day in tqdm(range(1, forecast_horizon_days + 1), desc="exp smoothing forecast", unit="day", leave=False):
            prediction = {"timestamp": (datetime.now() + timedelta(days=day)).isoformat(), "metrics": {}}

            for metric_name, values in tqdm(time_series.items(), desc="  metrics", unit="metric", leave=False):
                if len(values) >= 2:
                    # Simple exponential smoothing
                    alpha = 0.3  # Smoothing factor
                    smoothed_value = values[-1]

                    for i in range(len(values) - 2, -1, -1):
                        smoothed_value = alpha * values[i] + (1 - alpha) * smoothed_value

                    prediction["metrics"][metric_name] = smoothed_value
                else:
                    prediction["metrics"][metric_name] = 0.5

            predictions.append(prediction)

        return predictions

    def _arima_forecast(
        self, time_series: Dict[str, List[float]], forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast using ARIMA (simplified)."""
        # Simplified ARIMA implementation
        # In practice, would use proper ARIMA algorithm
        return self._linear_regression_forecast(time_series, forecast_horizon_days)

    def _lstm_forecast(
        self, time_series: Dict[str, List[float]], forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast using LSTM (simplified)."""
        # Simplified LSTM implementation
        # In practice, would use proper neural network
        return self._linear_regression_forecast(time_series, forecast_horizon_days)

    def _prophet_forecast(
        self, time_series: Dict[str, List[float]], forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast using Prophet (simplified)."""
        # Simplified Prophet implementation
        # In practice, would use proper Prophet algorithm
        return self._linear_regression_forecast(time_series, forecast_horizon_days)

    def _calculate_confidence_intervals(
        self, historical_data: Dict[str, List[float]], predictions: List[Dict[str, Any]]
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for predictions."""
        confidence_intervals = {}

        for metric_name in tqdm(historical_data.keys(), desc="confidence intervals", unit="metric", leave=False):
            values = historical_data[metric_name]

            if len(values) >= 3:
                # Calculate prediction intervals based on historical variance
                std_dev = np.std(values)
                margin = 1.96 * std_dev  # 95% confidence interval

                confidence_intervals[metric_name] = (max(0.0, 0.5 - margin), min(1.0, 0.5 + margin))
            else:
                confidence_intervals[metric_name] = (0.3, 0.7)  # Default interval

        return confidence_intervals

    def _calculate_model_accuracy(
        self, historical_data: Dict[str, List[float]], predictions: List[Dict[str, Any]]
    ) -> float:
        """Calculate forecast model accuracy."""
        if not historical_data or not predictions:
            return 0.5

        # Simple accuracy calculation based on prediction reasonableness
        total_accuracy = 0.0
        metric_count = 0

        for metric_name in tqdm(historical_data.keys(), desc="accuracy check", unit="metric", leave=False):
            if metric_name in predictions[0]["metrics"]:
                # Check if predictions are within reasonable bounds
                predicted_values = [p["metrics"][metric_name] for p in predictions[:5]]

                if predicted_values:
                    # Calculate mean absolute error against last historical value
                    last_value = historical_data[metric_name][-1]
                    mae = np.mean([abs(pred - last_value) for pred in predicted_values])
                    accuracy = max(0.0, 1.0 - mae)

                    total_accuracy += accuracy
                    metric_count += 1

        return total_accuracy / metric_count if metric_count > 0 else 0.5

    def _create_default_forecast(self, forecast_horizon_days: int) -> TemporalForecast:
        """Create default forecast when insufficient data is available."""
        predictions = []

        for day in range(1, forecast_horizon_days + 1):
            prediction = {
                "timestamp": (datetime.now() + timedelta(days=day)).isoformat(),
                "metrics": {"complexity_score": 0.5, "activity_level": 0.5, "risk_score": 0.5},
            }
            predictions.append(prediction)

        return TemporalForecast(
            forecast_id=f"default_forecast_{int(time.time())}",
            forecast_horizon=timedelta(days=forecast_horizon_days),
            predictions=predictions,
            confidence_intervals={
                "complexity_score": (0.3, 0.7),
                "activity_level": (0.3, 0.7),
                "risk_score": (0.3, 0.7),
            },
            model_accuracy=0.5,
            generated_at=datetime.now(),
        )

    def _calculate_statistical_baselines(self, data: List[TemporalPoint]) -> Dict[str, Dict[str, float]]:
        """Calculate statistical baselines from historical data."""
        baselines = {}

        # Collect all metric values
        metric_values = defaultdict(list)
        for point in data:
            for metric_name, value in point.metrics.items():
                metric_values[metric_name].append(value)

        # Calculate baseline statistics
        for metric_name, values in metric_values.items():
            if len(values) >= 2:
                baselines[metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                }

        return baselines

    def _detect_pattern_anomalies(
        self, data: List[TemporalPoint], sensitivity: float
    ) -> List[Dict[str, Any]]:
        """Detect pattern-based anomalies."""
        anomalies = []

        # Check for deviations from detected patterns
        for pattern in tqdm(self.temporal_patterns.values(), desc="pattern anomaly scan", unit="pattern", leave=False):
            if pattern.strength > 0.7:  # Strong patterns
                # Check if recent data follows the pattern
                recent_points = data[-5:]  # Last 5 points

                for point in tqdm(recent_points, desc="  recent points", unit="pt", leave=False):
                    pattern_compliance = self._check_pattern_compliance(point, pattern)

                    if pattern_compliance < (1.0 - sensitivity):
                        anomaly = {
                            "type": "pattern_anomaly",
                            "pattern_id": pattern.pattern_id,
                            "pattern_type": pattern.pattern_type.value,
                            "compliance": pattern_compliance,
                            "severity": "high" if pattern_compliance < 0.3 else "medium",
                            "timestamp": point.timestamp.isoformat(),
                        }
                        anomalies.append(anomaly)

        return anomalies

    def _check_pattern_compliance(self, point: TemporalPoint, pattern: TemporalPattern) -> float:
        """Check if a point complies with a pattern."""
        # Simplified pattern compliance check
        # In practice, would use more sophisticated pattern matching

        if pattern.pattern_type == TemporalPattern.SEASONAL:
            # Check if point occurs at expected time
            if pattern.periodicity:
                expected_time = point.timestamp.time()
                pattern_start_time = pattern.start_time.time()

                # Allow some tolerance
                time_diff = abs((expected_time.hour - pattern_start_time.hour) % 24)
                compliance = 1.0 - (time_diff / 12.0)  # Normalize to 0-1
                return max(0.0, compliance)

        elif pattern.pattern_type == TemporalPattern.TREND:
            # Check if point follows trend direction
            if len(pattern.supporting_points) >= 2:
                first_point = pattern.supporting_points[0]
                last_point = pattern.supporting_points[-1]

                # Extract a key metric for trend comparison
                metric_name = "complexity_score"
                if (
                    metric_name in first_point.metrics
                    and metric_name in last_point.metrics
                    and metric_name in point.metrics
                ):
                    trend_direction = last_point.metrics[metric_name] - first_point.metrics[metric_name]
                    current_direction = point.metrics[metric_name] - last_point.metrics[metric_name]

                    # Check if current direction matches trend
                    if trend_direction * current_direction >= 0:
                        return 0.8
                    else:
                        return 0.3

        # Default compliance
        return 0.7

    def get_temporal_statistics(self) -> Dict[str, Any]:
        """Get temporal intelligence statistics."""
        return {
            "total_temporal_points": len(self.temporal_data),
            "detected_patterns": len(self.temporal_patterns),
            "causal_relationships": len(self.causal_relationships),
            "pattern_types": {
                pattern_type.value: len(
                    [p for p in self.temporal_patterns.values() if p.pattern_type == pattern_type]
                )
                for pattern_type in TemporalPattern
            },
            "causality_types": {
                causality_type.value: len(
                    [r for r in self.causal_relationships.values() if r.causality_type == causality_type]
                )
                for causality_type in CausalityType
            },
            "available_models": list(self.forecasting_models.keys()),
        }
