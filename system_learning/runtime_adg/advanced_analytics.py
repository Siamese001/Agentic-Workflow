"""Advanced Runtime ADG Analytics - Pattern analysis and optimization insights.

Provides sophisticated analysis of Runtime ADG snapshots to identify patterns,
performance bottlenecks, and optimization opportunities.

FEATURES:
- Advanced pattern detection and analysis
- Performance bottleneck identification
- Anomaly detection in execution patterns
- Optimization recommendations
- Trend analysis over time
- Predictive analytics for system behavior

USAGE:
    analyzer = AdvancedADGAnalytics()
    insights = analyzer.analyze_snapshot(snapshot)
    recommendations = analyzer.get_optimization_recommendations(insights)
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from system_learning.runtime_adg import (
    RuntimeADGSnapshot,
)

emit_determinism_digest("advanced_adg_analytics", "advanced_adg_analytics_digest")
record_execution_trace("advanced_adg_analytics", "advanced_adg_analytics_trace")

Logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for Runtime ADG analysis."""

    total_duration_ms: float = 0.0
    avg_node_duration_ms: float = 0.0
    max_node_duration_ms: float = 0.0
    min_node_duration_ms: float = float('inf')
    bottleneck_nodes: list[dict[str, Any]] = field(default_factory=list)
    slow_operations: list[dict[str, Any]] = field(default_factory=list)
    fast_operations: list[dict[str, Any]] = field(default_factory=list)
    critical_path_duration_ms: float = 0.0
    parallelism_factor: float = 0.0


@dataclass
class PatternMetrics:
    """Pattern analysis metrics."""

    layer_distribution: dict[str, int] = field(default_factory=dict)
    component_distribution: dict[str, int] = field(default_factory=dict)
    span_type_distribution: dict[str, int] = field(default_factory=dict)
    error_patterns: list[dict[str, Any]] = field(default_factory=list)
    timing_patterns: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    relation_patterns: dict[str, int] = field(default_factory=dict)
    anomaly_patterns: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class OptimizationInsights:
    """Optimization insights and recommendations."""

    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    pattern_metrics: PatternMetrics = field(default_factory=PatternMetrics)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    risk_factors: list[dict[str, Any]] = field(default_factory=list)
    efficiency_score: float = 0.0
    complexity_score: float = 0.0
    reliability_score: float = 0.0


class AdvancedADGAnalytics:
    """
    Advanced analytics engine for Runtime ADG snapshots.

    Provides sophisticated pattern analysis, performance optimization,
    and predictive analytics capabilities.
    """

    def __init__(self) -> None:
        """Initialize advanced analytics engine."""
        self._analysis_cache: dict[str, OptimizationInsights] = {}
        self._historical_patterns: list[dict[str, Any]] = []
        self._performance_baselines: dict[str, float] = {}
        self._anomaly_thresholds: dict[str, float] = {
            "slow_operation_threshold_ms": 1000.0,
            "fast_operation_threshold_ms": 10.0,
            "error_rate_threshold": 0.05,
            "complexity_threshold": 100,
        }

    def analyze_snapshot(self, snapshot: RuntimeADGSnapshot) -> OptimizationInsights:
        """
        Perform comprehensive analysis of a Runtime ADG snapshot.

        Args:
            snapshot: Runtime ADG snapshot to analyze

        Returns:
            Comprehensive optimization insights
        """
        cache_key = f"{snapshot.trace_id}_{snapshot.started_at_utc}"

        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        insights = OptimizationInsights()

        # Performance analysis
        insights.performance_metrics = self._analyze_performance(snapshot)

        # Pattern analysis
        insights.pattern_metrics = self._analyze_patterns(snapshot)

        # Generate recommendations
        insights.recommendations = self._generate_recommendations(insights)

        # Identify risk factors
        insights.risk_factors = self._identify_risk_factors(insights)

        # Calculate scores
        insights.efficiency_score = self._calculate_efficiency_score(insights)
        insights.complexity_score = self._calculate_complexity_score(insights)
        insights.reliability_score = self._calculate_reliability_score(insights)

        # Cache results
        self._analysis_cache[cache_key] = insights

        # Store historical patterns
        self._store_historical_patterns(insights)

        Logger.info(f"[ADVANCED_ANALYTICS] Analyzed snapshot {snapshot.trace_id}")

        return insights

    def _analyze_performance(self, snapshot: RuntimeADGSnapshot) -> PerformanceMetrics:
        """Analyze performance metrics from snapshot."""
        metrics = PerformanceMetrics()

        if not snapshot.nodes:
            return metrics

        # Calculate duration statistics
        durations = [node.duration_ms for node in snapshot.nodes if node.duration_ms is not None]

        if durations:
            metrics.total_duration_ms = sum(durations)
            metrics.avg_node_duration_ms = statistics.mean(durations)
            metrics.max_node_duration_ms = max(durations)
            metrics.min_node_duration_ms = min(durations)

        # Identify bottlenecks (top 10% slowest operations)
        if durations:
            threshold = statistics.quantile(durations, 0.9)
            for node in snapshot.nodes:
                if node.duration_ms and node.duration_ms >= threshold:
                    metrics.bottleneck_nodes.append({
                        "node_id": node.node_id,
                        "component": node.component,
                        "layer": node.layer,
                        "duration_ms": node.duration_ms,
                        "operation": node.kind,
                    })

        # Identify slow and fast operations
        for node in snapshot.nodes:
            if node.duration_ms:
                if node.duration_ms > self._anomaly_thresholds["slow_operation_threshold_ms"]:
                    metrics.slow_operations.append({
                        "node_id": node.node_id,
                        "component": node.component,
                        "layer": node.layer,
                        "duration_ms": node.duration_ms,
                        "operation": node.kind,
                    })
                elif node.duration_ms < self._anomaly_thresholds["fast_operation_threshold_ms"]:
                    metrics.fast_operations.append({
                        "node_id": node.node_id,
                        "component": node.component,
                        "layer": node.layer,
                        "duration_ms": node.duration_ms,
                        "operation": node.kind,
                    })

        # Calculate critical path duration
        metrics.critical_path_duration_ms = self._calculate_critical_path(snapshot)

        # Calculate parallelism factor
        metrics.parallelism_factor = self._calculate_parallelism_factor(snapshot)

        return metrics

    def _analyze_patterns(self, snapshot: RuntimeADGSnapshot) -> PatternMetrics:
        """Analyze patterns in snapshot."""
        patterns = PatternMetrics()

        # Node-based patterns
        for node in snapshot.nodes:
            # Layer distribution
            patterns.layer_distribution[node.layer] = patterns.layer_distribution.get(node.layer, 0) + 1

            # Component distribution
            patterns.component_distribution[node.component] = patterns.component_distribution.get(node.component, 0) + 1

            # Span type distribution
            patterns.span_type_distribution[node.kind] = patterns.span_type_distribution.get(node.kind, 0) + 1

            # Error patterns
            if hasattr(node, 'status') and node.status == "error":
                patterns.error_patterns.append({
                    "node_id": node.node_id,
                    "component": node.component,
                    "layer": node.layer,
                    "operation": node.kind,
                })

        # Edge-based patterns
        for edge in snapshot.edges:
            relation_type = edge.relation_type
            patterns.relation_patterns[relation_type] = patterns.relation_patterns.get(relation_type, 0) + 1

        # Timing patterns
        patterns.timing_patterns = {
            "slow_operations": [
                {
                    "node_id": node.node_id,
                    "component": node.component,
                    "duration_ms": node.duration_ms,
                }
                for node in snapshot.nodes
                if node.duration_ms and node.duration_ms > self._anomaly_thresholds["slow_operation_threshold_ms"]
            ],
            "fast_operations": [
                {
                    "node_id": node.node_id,
                    "component": node.component,
                    "duration_ms": node.duration_ms,
                }
                for node in snapshot.nodes
                if node.duration_ms and node.duration_ms < self._anomaly_thresholds["fast_operation_threshold_ms"]
            ],
        }

        # Detect anomalies
        patterns.anomaly_patterns = self._detect_anomalies(snapshot, patterns)

        return patterns

    def _generate_recommendations(self, insights: OptimizationInsights) -> list[dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []

        # Performance recommendations
        perf = insights.performance_metrics

        if perf.bottleneck_nodes:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "title": "Optimize Bottleneck Operations",
                "description": f"Found {len(perf.bottleneck_nodes)} bottleneck operations",
                "actions": [
                    "Profile slow operations for optimization opportunities",
                    "Consider caching frequently accessed data",
                    "Review algorithmic complexity",
                ],
                "affected_nodes": perf.bottleneck_nodes[:5],  # Top 5
            })

        if perf.slow_operations:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "title": "Investigate Slow Operations",
                "description": f"Found {len(perf.slow_operations)} slow operations (>1s)",
                "actions": [
                    "Add performance monitoring",
                    "Consider async processing",
                    "Review resource allocation",
                ],
                "affected_operations": perf.slow_operations[:3],
            })

        # Pattern recommendations
        patterns = insights.pattern_metrics

        if patterns.error_patterns:
            error_rate = len(patterns.error_patterns) / len(patterns.layer_distribution) if patterns.layer_distribution else 0
            if error_rate > self._anomaly_thresholds["error_rate_threshold"]:
                recommendations.append({
                    "type": "reliability",
                    "priority": "high",
                    "title": "High Error Rate Detected",
                    "description": f"Error rate: {error_rate:.2%}",
                    "actions": [
                        "Implement better error handling",
                        "Add circuit breakers",
                        "Review input validation",
                    ],
                    "error_patterns": patterns.error_patterns,
                })

        # Complexity recommendations
        if insights.complexity_score > self._anomaly_thresholds["complexity_threshold"]:
            recommendations.append({
                "type": "architecture",
                "priority": "medium",
                "title": "High Complexity Detected",
                "description": f"Complexity score: {insights.complexity_score:.1f}",
                "actions": [
                    "Consider breaking down complex operations",
                    "Review service boundaries",
                    "Implement design patterns for simplification",
                ],
            })

        # Parallelism recommendations
        if perf.parallelism_factor < 0.5:
            recommendations.append({
                "type": "performance",
                "priority": "low",
                "title": "Low Parallelism Detected",
                "description": f"Parallelism factor: {perf.parallelism_factor:.2f}",
                "actions": [
                    "Identify opportunities for parallel execution",
                    "Review sequential dependencies",
                    "Consider async processing patterns",
                ],
            })

        return recommendations

    def _identify_risk_factors(self, insights: OptimizationInsights) -> list[dict[str, Any]]:
        """Identify potential risk factors."""
        risks = []

        perf = insights.performance_metrics
        patterns = insights.pattern_metrics

        # Performance risks
        if perf.max_node_duration_ms > 5000:  # > 5 seconds
            risks.append({
                "type": "performance",
                "severity": "high",
                "description": "Very slow operation detected",
                "impact": "May cause timeouts and poor user experience",
                "mitigation": "Implement timeout handling and optimization",
            })

        # Reliability risks
        error_rate = len(patterns.error_patterns) / len(patterns.layer_distribution) if patterns.layer_distribution else 0
        if error_rate > 0.1:  # > 10% error rate
            risks.append({
                "type": "reliability",
                "severity": "high",
                "description": "High error rate",
                "impact": "System instability and poor reliability",
                "mitigation": "Implement comprehensive error handling",
            })

        # Complexity risks
        if insights.complexity_score > 200:
            risks.append({
                "type": "maintainability",
                "severity": "medium",
                "description": "High complexity",
                "impact": "Difficult to maintain and debug",
                "mitigation": "Refactor and simplify architecture",
            })

        # Resource risks
        if len(patterns.layer_distribution) > 50:
            risks.append({
                "type": "resource",
                "severity": "medium",
                "description": "High resource utilization",
                "impact": "Potential resource exhaustion",
                "mitigation": "Implement resource monitoring and limits",
            })

        return risks

    def _calculate_efficiency_score(self, insights: OptimizationInsights) -> float:
        """Calculate efficiency score (0-100)."""
        score = 100.0

        perf = insights.performance_metrics

        # Penalize slow operations
        if perf.slow_operations:
            score -= min(len(perf.slow_operations) * 5, 30)

        # Penalize bottlenecks
        if perf.bottleneck_nodes:
            score -= min(len(perf.bottleneck_nodes) * 10, 40)

        # Reward parallelism
        if perf.parallelism_factor > 0.5:
            score += (perf.parallelism_factor - 0.5) * 20

        # Reward fast operations
        if perf.fast_operations:
            score += min(len(perf.fast_operations) * 2, 10)

        return max(0.0, min(100.0, score))

    def _calculate_complexity_score(self, insights: OptimizationInsights) -> float:
        """Calculate complexity score."""
        patterns = insights.pattern_metrics

        score = 0.0

        # Node count contributes to complexity
        score += sum(patterns.layer_distribution.values()) * 2

        # Edge count contributes to complexity
        score += sum(patterns.relation_patterns.values()) * 3

        # Different components add complexity
        score += len(patterns.component_distribution) * 5

        # Different layers add complexity
        score += len(patterns.layer_distribution) * 10

        return score

    def _calculate_reliability_score(self, insights: OptimizationInsights) -> float:
        """Calculate reliability score (0-100)."""
        score = 100.0

        patterns = insights.pattern_metrics

        # Penalize errors
        if patterns.error_patterns:
            total_operations = sum(patterns.layer_distribution.values())
            error_rate = len(patterns.error_patterns) / total_operations if total_operations > 0 else 0
            score -= error_rate * 100

        # Penalize anomalies
        if patterns.anomaly_patterns:
            score -= len(patterns.anomaly_patterns) * 10

        return max(0.0, min(100.0, score))

    def _calculate_critical_path(self, snapshot: RuntimeADGSnapshot) -> float:
        """Calculate critical path duration."""
        # Simplified critical path calculation
        # In a real implementation, this would use graph algorithms

        max_duration = 0.0
        for node in snapshot.nodes:
            if node.duration_ms and node.duration_ms > max_duration:
                max_duration = node.duration_ms

        return max_duration

    def _calculate_parallelism_factor(self, snapshot: RuntimeADGSnapshot) -> float:
        """Calculate parallelism factor."""
        # Simplified parallelism calculation
        # In a real implementation, this would analyze the graph structure

        if not snapshot.nodes:
            return 0.0

        # Estimate parallelism based on concurrent operations
        concurrent_ops = 0
        max_concurrent = 0

        # This is a simplified version - real implementation would be more sophisticated
        for node in snapshot.nodes:
            if hasattr(node, 'start_time') and hasattr(node, 'end_time'):
                # Count overlapping operations
                concurrent_ops += 1
                max_concurrent = max(max_concurrent, concurrent_ops)

        return max_concurrent / len(snapshot.nodes) if snapshot.nodes else 0.0

    def _detect_anomalies(self, snapshot: RuntimeADGSnapshot, patterns: PatternMetrics) -> list[dict[str, Any]]:
        """Detect anomalies in the snapshot."""
        anomalies = []

        # Duration anomalies
        durations = [node.duration_ms for node in snapshot.nodes if node.duration_ms is not None]
        if durations:
            mean_duration = statistics.mean(durations)
            std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

            for node in snapshot.nodes:
                if node.duration_ms:
                    z_score = abs(node.duration_ms - mean_duration) / std_duration if std_duration > 0 else 0
                    if z_score > 3:  # 3 standard deviations
                        anomalies.append({
                            "type": "duration_anomaly",
                            "node_id": node.node_id,
                            "component": node.component,
                            "duration_ms": node.duration_ms,
                            "z_score": z_score,
                        })

        # Component frequency anomalies
        total_operations = sum(patterns.layer_distribution.values())
        for component, count in patterns.component_distribution.items():
            frequency = count / total_operations if total_operations > 0 else 0
            if frequency > 0.5:  # Component appears in >50% of operations
                anomalies.append({
                    "type": "frequency_anomaly",
                    "component": component,
                    "frequency": frequency,
                    "description": "Component appears unusually frequently",
                })

        return anomalies

    def _store_historical_patterns(self, insights: OptimizationInsights) -> None:
        """Store patterns for historical analysis."""
        pattern_data = {
            "timestamp": time.time(),
            "efficiency_score": insights.efficiency_score,
            "complexity_score": insights.complexity_score,
            "reliability_score": insights.reliability_score,
            "recommendation_count": len(insights.recommendations),
            "risk_count": len(insights.risk_factors),
        }

        self._historical_patterns.append(pattern_data)

        # Keep only last 1000 patterns
        if len(self._historical_patterns) > 1000:
            self._historical_patterns = self._historical_patterns[-1000:]

    def get_trend_analysis(self) -> dict[str, Any]:
        """Get trend analysis from historical patterns."""
        if len(self._historical_patterns) < 2:
            return {"message": "Insufficient historical data"}

        recent_patterns = self._historical_patterns[-10:]  # Last 10 patterns

        # Calculate trends
        efficiency_trend = self._calculate_trend([p["efficiency_score"] for p in recent_patterns])
        complexity_trend = self._calculate_trend([p["complexity_score"] for p in recent_patterns])
        reliability_trend = self._calculate_trend([p["reliability_score"] for p in recent_patterns])

        return {
            "efficiency_trend": efficiency_trend,
            "complexity_trend": complexity_trend,
            "reliability_trend": reliability_trend,
            "pattern_count": len(self._historical_patterns),
            "analysis_period": "last 10 snapshots",
        }

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"

        # Simple linear regression trend
        n = len(values)
        x = list(range(n))

        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "degrading"
        else:
            return "stable"

    def get_optimization_recommendations(self, insights: OptimizationInsights) -> list[dict[str, Any]]:
        """Get prioritized optimization recommendations."""
        # Sort recommendations by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}

        sorted_recommendations = sorted(
            insights.recommendations,
            key=lambda r: priority_order.get(r.get("priority", "low"), 1),
            reverse=True,
        )

        return sorted_recommendations

    def get_performance_baselines(self) -> dict[str, float]:
        """Get current performance baselines."""
        if not self._historical_patterns:
            return {}

        recent_patterns = self._historical_patterns[-50:]  # Last 50 patterns

        return {
            "avg_efficiency": statistics.mean([p["efficiency_score"] for p in recent_patterns]),
            "avg_complexity": statistics.mean([p["complexity_score"] for p in recent_patterns]),
            "avg_reliability": statistics.mean([p["reliability_score"] for p in recent_patterns]),
            "avg_recommendations": statistics.mean([p["recommendation_count"] for p in recent_patterns]),
        }


# Global analytics instance
_global_analytics: AdvancedADGAnalytics | None = None


def get_global_analytics() -> AdvancedADGAnalytics:
    """Get the global advanced analytics instance."""
    global _global_analytics
    if _global_analytics is None:
        _global_analytics = AdvancedADGAnalytics()
    return _global_analytics


def analyze_snapshot_for_insights(snapshot: RuntimeADGSnapshot) -> OptimizationInsights:
    """
    Analyze a snapshot for optimization insights.

    Args:
        snapshot: Runtime ADG snapshot to analyze

    Returns:
        Optimization insights and recommendations
    """
    analytics = get_global_analytics()
    return analytics.analyze_snapshot(snapshot)


def get_system_trends() -> dict[str, Any]:
    """Get system performance trends."""
    analytics = get_global_analytics()
    return analytics.get_trend_analysis()


def get_performance_recommendations(snapshot: RuntimeADGSnapshot) -> list[dict[str, Any]]:
    """
    Get performance optimization recommendations.

    Args:
        snapshot: Runtime ADG snapshot to analyze

    Returns:
        Prioritized optimization recommendations
    """
    insights = analyze_snapshot_for_insights(snapshot)
    return insights.recommendations
