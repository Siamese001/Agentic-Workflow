"""
L4 Feature Extractor

Extracts features for L4 performance optimization model including
system performance metrics, resource utilization, bottlenecks,
optimization opportunities, and performance trends.
"""

import math
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class L4FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L4 performance optimization.

    Extracts deterministic features for performance optimization:
    - System performance metrics and KPIs
    - Resource utilization and capacity metrics
    - Bottleneck identification and severity
    - Performance trends and patterns
    - Optimization opportunity scoring
    - Service level agreement compliance
    - Cost efficiency metrics
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l4_performance_optimizer")
        if not schema:
            # Create schema for L4 performance optimizer
            schema = self._create_l4_schema()
        super().__init__(schema)

    def _create_l4_schema(self) -> FeatureSchema:
        """Create feature schema for L4 performance optimizer."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="response_time_trend",
                feature_type=FeatureType.NUMERIC,
                description="Trend in response times over time window",
                provenance="performance.response_time.trend",
                validation_rules={"min_value": -1.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="throughput_variance",
                feature_type=FeatureType.NUMERIC,
                description="Variance in throughput metrics",
                provenance="performance.throughput.variance",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="cpu_utilization_avg",
                feature_type=FeatureType.NUMERIC,
                description="Average CPU utilization percentage",
                provenance="resource.cpu.utilization_avg",
                validation_rules={"min_value": 0.0, "max_value": 100.0}
            ),
            FeatureDefinition(
                name="memory_utilization_avg",
                feature_type=FeatureType.NUMERIC,
                description="Average memory utilization percentage",
                provenance="resource.memory.utilization_avg",
                validation_rules={"min_value": 0.0, "max_value": 100.0}
            ),
            FeatureDefinition(
                name="bottleneck_severity",
                feature_type=FeatureType.NUMERIC,
                description="Severity of identified bottlenecks",
                provenance="performance.bottleneck.severity",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="optimization_potential",
                feature_type=FeatureType.NUMERIC,
                description="Potential for performance optimization",
                provenance="performance.optimization.potential",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="sla_compliance_rate",
                feature_type=FeatureType.NUMERIC,
                description="Service level agreement compliance rate",
                provenance="performance.sla.compliance_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="error_rate_trend",
                feature_type=FeatureType.NUMERIC,
                description="Trend in error rates over time",
                provenance="performance.error_rate.trend",
                validation_rules={"min_value": -1.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="cost_efficiency_score",
                feature_type=FeatureType.NUMERIC,
                description="Cost efficiency of current performance",
                provenance="performance.cost.efficiency_score",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="resource_waste_ratio",
                feature_type=FeatureType.NUMERIC,
                description="Ratio of wasted resources to total resources",
                provenance="resource.waste.ratio",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="l4_performance_optimizer",
            schema_version="1.0",
            description="Features for L4 performance optimization model",
            features=features
        )

    def _register_extraction_functions(self) -> None:
        """Register L4-specific feature extraction functions."""
        self.register_extraction_function("response_time_trend", self._extract_response_time_trend)
        self.register_extraction_function("throughput_variance", self._extract_throughput_variance)
        self.register_extraction_function("cpu_utilization_avg", self._extract_cpu_utilization_avg)
        self.register_extraction_function("memory_utilization_avg", self._extract_memory_utilization_avg)
        self.register_extraction_function("bottleneck_severity", self._extract_bottleneck_severity)
        self.register_extraction_function("optimization_potential", self._extract_optimization_potential)
        self.register_extraction_function("sla_compliance_rate", self._extract_sla_compliance_rate)
        self.register_extraction_function("error_rate_trend", self._extract_error_rate_trend)
        self.register_extraction_function("cost_efficiency_score", self._extract_cost_efficiency_score)
        self.register_extraction_function("resource_waste_ratio", self._extract_resource_waste_ratio)

    def _extract_response_time_trend(self, context: dict[str, Any]) -> float:
        """Extract response time trend (-1.0 to 1.0, negative = improving)."""
        performance = context.get("performance", {})

        # Direct trend if provided
        if "response_time_trend" in performance:
            return float(performance["response_time_trend"])

        # Calculate from historical response times
        response_times = performance.get("historical_response_times", [])

        if len(response_times) < 2:
            return 0.0  # No trend data

        # Calculate trend using linear regression slope
        n = len(response_times)
        if n < 5:  # Need sufficient data points
            return 0.0

        # Simple trend calculation: compare recent vs older average
        recent_count = min(5, n // 3)
        recent_avg = sum(response_times[-recent_count:]) / recent_count
        older_avg = sum(response_times[:-recent_count]) / (n - recent_count)

        # Normalize trend (-1 to 1)
        if older_avg > 0:
            trend = (recent_avg - older_avg) / older_avg
            # Clamp to reasonable range
            trend = max(-1.0, min(1.0, trend))
        else:
            trend = 0.0

        return round(trend, 3)

    def _extract_throughput_variance(self, context: dict[str, Any]) -> float:
        """Extract throughput variance (0.0 to 1.0)."""
        performance = context.get("performance", {})

        # Direct variance if provided
        if "throughput_variance" in performance:
            return float(performance["throughput_variance"])

        # Calculate from throughput data
        throughput_data = performance.get("throughput_data", [])

        if len(throughput_data) < 2:
            return 0.0  # No variance data

        # Calculate coefficient of variation
        mean_throughput = sum(throughput_data) / len(throughput_data)

        if mean_throughput > 0:
            variance = sum((x - mean_throughput) ** 2 for x in throughput_data) / len(throughput_data)
            std_dev = math.sqrt(variance)
            cv = std_dev / mean_throughput  # Coefficient of variation

            # Normalize to 0-1 range (CV > 1 is considered high variance)
            normalized_variance = min(1.0, cv)
        else:
            normalized_variance = 0.0

        return round(normalized_variance, 3)

    def _extract_cpu_utilization_avg(self, context: dict[str, Any]) -> float:
        """Extract average CPU utilization (0.0 to 100.0)."""
        resources = context.get("resources", {})

        # Direct utilization if provided
        if "cpu_utilization_avg" in resources:
            return float(resources["cpu_utilization_avg"])

        # Calculate from CPU utilization data
        cpu_data = resources.get("cpu_utilization_history", [])

        if not cpu_data:
            return 0.0

        avg_utilization = sum(cpu_data) / len(cpu_data)
        return round(max(0.0, min(100.0, avg_utilization)), 3)

    def _extract_memory_utilization_avg(self, context: dict[str, Any]) -> float:
        """Extract average memory utilization (0.0 to 100.0)."""
        resources = context.get("resources", {})

        # Direct utilization if provided
        if "memory_utilization_avg" in resources:
            return float(resources["memory_utilization_avg"])

        # Calculate from memory utilization data
        memory_data = resources.get("memory_utilization_history", [])

        if not memory_data:
            return 0.0

        avg_utilization = sum(memory_data) / len(memory_data)
        return round(max(0.0, min(100.0, avg_utilization)), 3)

    def _extract_bottleneck_severity(self, context: dict[str, Any]) -> float:
        """Extract bottleneck severity (0.0 to 1.0)."""
        performance = context.get("performance", {})

        # Direct severity if provided
        if "bottleneck_severity" in performance:
            return float(performance["bottleneck_severity"])

        # Calculate from bottleneck indicators
        bottlenecks = performance.get("bottlenecks", [])

        if not bottlenecks:
            return 0.0  # No bottlenecks

        # Weight bottleneck types by severity
        severity_weights = {
            "cpu": 0.3,
            "memory": 0.25,
            "io": 0.2,
            "network": 0.15,
            "database": 0.1
        }

        total_severity = 0.0
        for bottleneck in bottlenecks:
            bottleneck_type = bottleneck.get("type", "unknown")
            bottleneck_severity = bottleneck.get("severity", 0.5)  # 0-1 scale

            weight = severity_weights.get(bottleneck_type, 0.1)
            total_severity += bottleneck_severity * weight

        # Normalize by maximum possible severity
        max_possible_severity = sum(severity_weights.values())
        normalized_severity = total_severity / max_possible_severity

        return round(min(1.0, normalized_severity), 3)

    def _extract_optimization_potential(self, context: dict[str, Any]) -> float:
        """Extract optimization potential (0.0 to 1.0)."""
        performance = context.get("performance", {})

        # Direct potential if provided
        if "optimization_potential" in performance:
            return float(performance["optimization_potential"])

        # Calculate from various optimization indicators
        indicators = {
            "high_response_times": 0.3,
            "low_throughput": 0.25,
            "resource_underutilization": 0.2,
            "frequent_errors": 0.15,
            "sla_violations": 0.1
        }

        potential_score = 0.0

        # High response times
        response_times = performance.get("historical_response_times", [])
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            target_response_time = performance.get("target_response_time", 1000)  # 1 second default

            if avg_response_time > target_response_time:
                excess_ratio = (avg_response_time - target_response_time) / target_response_time
                potential_score += indicators["high_response_times"] * min(1.0, excess_ratio)

        # Low throughput
        throughput_data = performance.get("throughput_data", [])
        if throughput_data:
            avg_throughput = sum(throughput_data) / len(throughput_data)
            target_throughput = performance.get("target_throughput", 1000)

            if avg_throughput < target_throughput:
                deficit_ratio = (target_throughput - avg_throughput) / target_throughput
                potential_score += indicators["low_throughput"] * min(1.0, deficit_ratio)

        # Resource underutilization
        resources = context.get("resources", {})
        cpu_util = resources.get("cpu_utilization_avg", 0)
        memory_util = resources.get("memory_utilization_avg", 0)

        # Underutilization is when resources are < 50% utilized
        underutilization_score = max(0, (50 - cpu_util) / 50) * 0.5 + max(0, (50 - memory_util) / 50) * 0.5
        potential_score += indicators["resource_underutilization"] * underutilization_score

        # Frequent errors
        error_rates = performance.get("error_rates", [])
        if error_rates:
            avg_error_rate = sum(error_rates) / len(error_rates)
            if avg_error_rate > 0.01:  # > 1% error rate
                potential_score += indicators["frequent_errors"] * min(1.0, avg_error_rate * 100)

        # SLA violations
        sla_violations = performance.get("sla_violations", 0)
        total_requests = performance.get("total_requests", 1)

        if total_requests > 0:
            violation_rate = sla_violations / total_requests
            potential_score += indicators["sla_violations"] * min(1.0, violation_rate * 10)  # Scale up impact

        return round(min(1.0, potential_score), 3)

    def _extract_sla_compliance_rate(self, context: dict[str, Any]) -> float:
        """Extract SLA compliance rate (0.0 to 1.0)."""
        performance = context.get("performance", {})

        # Direct compliance rate if provided
        if "sla_compliance_rate" in performance:
            return float(performance["sla_compliance_rate"])

        # Calculate from SLA data
        sla_violations = performance.get("sla_violations", 0)
        total_requests = performance.get("total_requests", 1)

        compliance_rate = 1.0 - (sla_violations / max(1, total_requests))
        return round(max(0.0, min(1.0, compliance_rate)), 3)

    def _extract_error_rate_trend(self, context: dict[str, Any]) -> float:
        """Extract error rate trend (-1.0 to 1.0, negative = improving)."""
        performance = context.get("performance", {})

        # Direct trend if provided
        if "error_rate_trend" in performance:
            return float(performance["error_rate_trend"])

        # Calculate from error rate history
        error_rates = performance.get("error_rates", [])

        if len(error_rates) < 2:
            return 0.0  # No trend data

        # Calculate trend similar to response time trend
        n = len(error_rates)
        if n < 5:
            return 0.0

        recent_count = min(5, n // 3)
        recent_avg = sum(error_rates[-recent_count:]) / recent_count
        older_avg = sum(error_rates[:-recent_count]) / (n - recent_count)

        if older_avg > 0:
            trend = (recent_avg - older_avg) / older_avg
            trend = max(-1.0, min(1.0, trend))
        else:
            trend = 0.0

        return round(trend, 3)

    def _extract_cost_efficiency_score(self, context: dict[str, Any]) -> float:
        """Extract cost efficiency score (0.0 to 1.0)."""
        performance = context.get("performance", {})

        # Direct score if provided
        if "cost_efficiency_score" in performance:
            return float(performance["cost_efficiency_score"])

        # Calculate from cost and performance metrics
        current_cost = performance.get("current_cost", 0)
        baseline_cost = performance.get("baseline_cost", 1)

        if baseline_cost <= 0:
            return 0.5  # Default if no baseline

        # Cost efficiency = baseline_cost / current_cost, adjusted for performance
        cost_ratio = baseline_cost / current_cost

        # Adjust for performance (SLA compliance)
        sla_compliance = self._extract_sla_compliance_rate(context)

        # Combine cost ratio with performance
        efficiency_score = (cost_ratio * 0.6) + (sla_compliance * 0.4)

        return round(max(0.0, min(1.0, efficiency_score)), 3)

    def _extract_resource_waste_ratio(self, context: dict[str, Any]) -> float:
        """Extract resource waste ratio (0.0 to 1.0)."""
        resources = context.get("resources", {})

        # Direct ratio if provided
        if "resource_waste_ratio" in resources:
            return float(resources["resource_waste_ratio"])

        # Calculate from resource utilization
        cpu_util = resources.get("cpu_utilization_avg", 0)
        memory_util = resources.get("memory_utilization_avg", 0)

        # Waste is the inverse of utilization (below 50% is considered waste)
        cpu_waste = max(0, (50 - cpu_util) / 50) if cpu_util < 50 else 0
        memory_waste = max(0, (50 - memory_util) / 50) if memory_util < 50 else 0

        # Combine waste metrics
        total_waste = (cpu_waste + memory_waste) / 2

        return round(min(1.0, total_waste), 3)
