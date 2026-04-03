"""
L1 Feature Extractor

Extracts features for L1 capacity planning model including
traffic patterns, resource demand forecasts, scaling requirements,
capacity utilization trends, and provisioning recommendations.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any

from .base_extractor import DeterministicFeatureExtractor
from ..config.feature_schemas import FeatureSchemas, FeatureSchema


class L1FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L1 capacity planning.

    Extracts deterministic features for capacity planning:
    - Traffic patterns and demand forecasts
    - Resource utilization trends
    - Scaling requirements and recommendations
    - Capacity utilization metrics
    - Seasonal patterns and anomalies
    - Cost optimization opportunities
    - Performance impact predictions
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l1_capacity_planner")
        if not schema:
            # Create schema for L1 capacity planner
            schema = self._create_l1_schema()
        super().__init__(schema)

    def _create_l1_schema(self) -> FeatureSchema:
        """Create feature schema for L1 capacity planner."""
        from ..config.feature_schemas import FeatureSchema, FeatureDefinition, FeatureType

        features = [
            FeatureDefinition(
                name="traffic_growth_rate",
                feature_type=FeatureType.NUMERIC,
                description="Growth rate of traffic over time window",
                provenance="traffic.growth.rate",
                validation_rules={"min_value": -1.0, "max_value": 5.0}
            ),
            FeatureDefinition(
                name="demand_volatility",
                feature_type=FeatureType.NUMERIC,
                description="Volatility in demand patterns",
                provenance="demand.volatility",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="current_capacity_utilization",
                feature_type=FeatureType.NUMERIC,
                description="Current capacity utilization percentage",
                provenance="capacity.utilization.current",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="peak_demand_ratio",
                feature_type=FeatureType.NUMERIC,
                description="Ratio of peak to average demand",
                provenance="demand.peak_ratio",
                validation_rules={"min_value": 1.0, "max_value": 10.0}
            ),
            FeatureDefinition(
                name="scaling_frequency",
                feature_type=FeatureType.NUMERIC,
                description="Frequency of scaling events per day",
                provenance="scaling.frequency",
                validation_rules={"min_value": 0.0, "max_value": 100.0}
            ),
            FeatureDefinition(
                name="seasonal_pattern_strength",
                feature_type=FeatureType.NUMERIC,
                description="Strength of seasonal patterns in demand",
                provenance="seasonal.pattern_strength",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="forecast_accuracy",
                feature_type=FeatureType.NUMERIC,
                description="Accuracy of demand forecasts",
                provenance="forecast.accuracy",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="resource_efficiency",
                feature_type=FeatureType.NUMERIC,
                description="Efficiency of resource utilization",
                provenance="resource.efficiency",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="cost_per_request",
                feature_type=FeatureType.NUMERIC,
                description="Cost per request in current configuration",
                provenance="cost.per_request",
                validation_rules={"min_value": 0.0, "max_value": 1000.0}
            ),
            FeatureDefinition(
                name="capacity_buffer",
                feature_type=FeatureType.NUMERIC,
                description="Current capacity buffer percentage",
                provenance="capacity.buffer",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="l1_capacity_planner",
            schema_version="1.0",
            description="Features for L1 capacity planning model",
            features=features
        )

    def _register_extraction_functions(self) -> None:
        """Register L1-specific feature extraction functions."""
        self.register_extraction_function("traffic_growth_rate", self._extract_traffic_growth_rate)
        self.register_extraction_function("demand_volatility", self._extract_demand_volatility)
        self.register_extraction_function("current_capacity_utilization", self._extract_current_capacity_utilization)
        self.register_extraction_function("peak_demand_ratio", self._extract_peak_demand_ratio)
        self.register_extraction_function("scaling_frequency", self._extract_scaling_frequency)
        self.register_extraction_function("seasonal_pattern_strength", self._extract_seasonal_pattern_strength)
        self.register_extraction_function("forecast_accuracy", self._extract_forecast_accuracy)
        self.register_extraction_function("resource_efficiency", self._extract_resource_efficiency)
        self.register_extraction_function("cost_per_request", self._extract_cost_per_request)
        self.register_extraction_function("capacity_buffer", self._extract_capacity_buffer)

    def _extract_traffic_growth_rate(self, context: Dict[str, Any]) -> float:
        """Extract traffic growth rate (-1.0 to 5.0)."""
        traffic = context.get("traffic", {})

        # Direct growth rate if provided
        if "growth_rate" in traffic:
            return float(traffic["growth_rate"])

        # Calculate from historical traffic data
        traffic_history = traffic.get("historical_traffic", [])

        if len(traffic_history) < 2:
            return 0.0  # No growth data

        # Calculate growth rate over the period
        n = len(traffic_history)
        if n < 7:  # Need at least a week of data
            return 0.0

        # Compare recent period vs older period
        recent_period = min(7, n // 3)
        recent_avg = sum(traffic_history[-recent_period:]) / recent_period
        older_avg = sum(traffic_history[:-recent_period]) / (n - recent_period)

        if older_avg > 0:
            growth_rate = (recent_avg - older_avg) / older_avg
            # Annualize if data is daily (assuming daily data)
            if traffic.get("data_granularity") == "daily":
                growth_rate = growth_rate * 365
            elif traffic.get("data_granularity") == "hourly":
                growth_rate = growth_rate * 8760

            # Clamp to reasonable range
            growth_rate = max(-1.0, min(5.0, growth_rate))
        else:
            growth_rate = 0.0

        return round(growth_rate, 3)

    def _extract_demand_volatility(self, context: Dict[str, Any]) -> float:
        """Extract demand volatility (0.0 to 1.0)."""
        demand = context.get("demand", {})

        # Direct volatility if provided
        if "volatility" in demand:
            return float(demand["volatility"])

        # Calculate from demand data
        demand_data = demand.get("historical_demand", [])

        if len(demand_data) < 2:
            return 0.0  # No volatility data

        # Calculate coefficient of variation
        mean_demand = sum(demand_data) / len(demand_data)

        if mean_demand > 0:
            variance = sum((x - mean_demand) ** 2 for x in demand_data) / len(demand_data)
            std_dev = math.sqrt(variance)
            cv = std_dev / mean_demand  # Coefficient of variation

            # Normalize to 0-1 range (CV > 1 is considered high volatility)
            volatility = min(1.0, cv)
        else:
            volatility = 0.0

        return round(volatility, 3)

    def _extract_current_capacity_utilization(self, context: Dict[str, Any]) -> float:
        """Extract current capacity utilization (0.0 to 1.0)."""
        capacity = context.get("capacity", {})

        # Direct utilization if provided
        if "current_utilization" in capacity:
            return float(capacity["current_utilization"])

        # Calculate from current demand and maximum capacity
        current_demand = capacity.get("current_demand", 0)
        max_capacity = capacity.get("max_capacity", 1)

        if max_capacity > 0:
            utilization = current_demand / max_capacity
        else:
            utilization = 0.0

        return round(max(0.0, min(1.0, utilization)), 3)

    def _extract_peak_demand_ratio(self, context: Dict[str, Any]) -> float:
        """Extract peak to average demand ratio (1.0 to 10.0)."""
        demand = context.get("demand", {})

        # Direct ratio if provided
        if "peak_ratio" in demand:
            return float(demand["peak_ratio"])

        # Calculate from demand data
        demand_data = demand.get("historical_demand", [])

        if len(demand_data) < 2:
            return 1.0  # No peak data

        avg_demand = sum(demand_data) / len(demand_data)
        peak_demand = max(demand_data)

        if avg_demand > 0:
            peak_ratio = peak_demand / avg_demand
        else:
            peak_ratio = 1.0

        return round(max(1.0, min(10.0, peak_ratio)), 3)

    def _extract_scaling_frequency(self, context: Dict[str, Any]) -> float:
        """Extract scaling frequency per day (0.0 to 100.0)."""
        scaling = context.get("scaling", {})

        # Direct frequency if provided
        if "frequency_per_day" in scaling:
            return float(scaling["frequency_per_day"])

        # Calculate from scaling events
        scaling_events = scaling.get("historical_events", [])

        if not scaling_events:
            return 0.0

        # Count events in the last 24 hours
        now = datetime.now()
        day_ago = now - timedelta(days=1)

        recent_events = [
            event for event in scaling_events
            if event.get("timestamp")
            and isinstance(event["timestamp"], str)
            and datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00')) > day_ago
        ]

        frequency = len(recent_events)
        return round(min(100.0, frequency), 3)

    def _extract_seasonal_pattern_strength(self, context: Dict[str, Any]) -> float:
        """Extract seasonal pattern strength (0.0 to 1.0)."""
        seasonal = context.get("seasonal", {})

        # Direct strength if provided
        if "pattern_strength" in seasonal:
            return float(seasonal["pattern_strength"])

        # Calculate from seasonal data
        seasonal_data = seasonal.get("seasonal_patterns", [])

        if not seasonal_data:
            return 0.0  # No seasonal data

        # Simple seasonal strength calculation based on variance
        # between different periods (e.g., weekdays vs weekends, months)
        if len(seasonal_data) >= 2:
            values = [pattern.get("value", 0) for pattern in seasonal_data]
            mean_value = sum(values) / len(values)

            if mean_value > 0:
                variance = sum((x - mean_value) ** 2 for x in values) / len(values)
                std_dev = math.sqrt(variance)
                cv = std_dev / mean_value

                # Normalize to 0-1 range
                pattern_strength = min(1.0, cv)
            else:
                pattern_strength = 0.0
        else:
            pattern_strength = 0.0

        return round(pattern_strength, 3)

    def _extract_forecast_accuracy(self, context: Dict[str, Any]) -> float:
        """Extract forecast accuracy (0.0 to 1.0)."""
        forecast = context.get("forecast", {})

        # Direct accuracy if provided
        if "accuracy" in forecast:
            return float(forecast["accuracy"])

        # Calculate from forecast vs actual data
        forecast_values = forecast.get("forecast_values", [])
        actual_values = forecast.get("actual_values", [])

        if len(forecast_values) != len(actual_values) or len(forecast_values) == 0:
            return 0.5  # Default if no comparison data

        # Calculate Mean Absolute Percentage Error (MAPE)
        total_ape = 0.0
        valid_count = 0

        for forecast_val, actual_val in zip(forecast_values, actual_values):
            if actual_val != 0:
                ape = abs(forecast_val - actual_val) / abs(actual_val)
                total_ape += ape
                valid_count += 1

        if valid_count > 0:
            mape = total_ape / valid_count
            accuracy = max(0.0, 1.0 - mape)  # Convert error to accuracy
        else:
            accuracy = 0.5

        return round(max(0.0, min(1.0, accuracy)), 3)

    def _extract_resource_efficiency(self, context: Dict[str, Any]) -> float:
        """Extract resource efficiency (0.0 to 1.0)."""
        resources = context.get("resources", {})

        # Direct efficiency if provided
        if "efficiency" in resources:
            return float(resources["efficiency"])

        # Calculate from utilization and performance metrics
        utilization = resources.get("utilization", 0.5)  # 0-1 scale
        performance = resources.get("performance_score", 0.5)  # 0-1 scale

        # Efficiency is a combination of utilization and performance
        # High efficiency means good utilization with good performance
        efficiency = (utilization * 0.6) + (performance * 0.4)

        return round(max(0.0, min(1.0, efficiency)), 3)

    def _extract_cost_per_request(self, context: Dict[str, Any]) -> float:
        """Extract cost per request (0.0 to 1000.0)."""
        cost = context.get("cost", {})

        # Direct cost if provided
        if "cost_per_request" in cost:
            return float(cost["cost_per_request"])

        # Calculate from total cost and request count
        total_cost = cost.get("total_cost", 0)
        request_count = cost.get("request_count", 1)

        if request_count > 0:
            cost_per_request = total_cost / request_count
        else:
            cost_per_request = 0.0

        return round(max(0.0, min(1000.0, cost_per_request)), 3)

    def _extract_capacity_buffer(self, context: Dict[str, Any]) -> float:
        """Extract capacity buffer percentage (0.0 to 1.0)."""
        capacity = context.get("capacity", {})

        # Direct buffer if provided
        if "buffer_percentage" in capacity:
            return float(capacity["buffer_percentage"])

        # Calculate from current utilization and target utilization
        current_util = self._extract_current_capacity_utilization(context)
        target_util = capacity.get("target_utilization", 0.8)  # 80% target

        if current_util < target_util:
            buffer = (target_util - current_util) / target_util
        else:
            buffer = 0.0  # No buffer if over target

        return round(max(0.0, min(1.0, buffer)), 3)
