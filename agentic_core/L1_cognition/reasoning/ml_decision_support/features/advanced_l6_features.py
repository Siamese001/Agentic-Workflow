"""
Advanced L6 Feature Extractor

Extracts enhanced features for L6 advanced anomaly detection model including
behavioral patterns, system metrics, anomaly indicators,
and detection optimization signals.
"""

from datetime import datetime
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class AdvancedL6FeatureExtractor(DeterministicFeatureExtractor):
    """
    Advanced feature extractor for L6 autoencoder anomaly detection.

    Extracts enhanced deterministic features for advanced anomaly detection:
    - Behavioral patterns and deviation analysis
    - System metrics and performance indicators
    - Temporal patterns and trend analysis
    - Reconstruction error and anomaly scores
    - Multi-dimensional anomaly indicators
    - Contextual anomaly detection signals
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("advanced_l6_detector")
        if not schema:
            # Create schema for advanced L6 detector
            schema = self._create_advanced_l6_schema()
        super().__init__(schema)

    def _create_advanced_l6_schema(self) -> FeatureSchema:
        """Create feature schema for advanced L6 detector."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="behavioral_deviation",
                feature_type=FeatureType.NUMERIC,
                description="Deviation from normal behavioral patterns",
                provenance="anomaly.behavioral.deviation",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="system_metric_anomaly",
                feature_type=FeatureType.NUMERIC,
                description="Anomaly score from system metrics",
                provenance="anomaly.system.metric_anomaly",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="temporal_pattern_break",
                feature_type=FeatureType.NUMERIC,
                description="Break in temporal patterns",
                provenance="anomaly.temporal.pattern_break",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="reconstruction_error",
                feature_type=FeatureType.NUMERIC,
                description="Autoencoder reconstruction error",
                provenance="anomaly.autoencoder.reconstruction_error",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="multivariate_anomaly",
                feature_type=FeatureType.NUMERIC,
                description="Multivariate anomaly detection score",
                provenance="anomaly.multivariate.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="contextual_anomaly",
                feature_type=FeatureType.NUMERIC,
                description="Contextual anomaly detection score",
                provenance="anomaly.contextual.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="performance_degradation",
                feature_type=FeatureType.NUMERIC,
                description="Performance degradation indicator",
                provenance="anomaly.performance.degradation",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="resource_anomaly",
                feature_type=FeatureType.NUMERIC,
                description="Resource usage anomaly score",
                provenance="anomaly.resource.anomaly",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="security_anomaly",
                feature_type=FeatureType.NUMERIC,
                description="Security-related anomaly score",
                provenance="anomaly.security.anomaly",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="anomaly_confidence",
                feature_type=FeatureType.NUMERIC,
                description="Overall confidence in anomaly detection",
                provenance="anomaly.overall.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
        ]

        return FeatureSchema(
            schema_name="advanced_l6_detector",
            schema_version="1.0",
            description="Enhanced features for L6 autoencoder anomaly detection model",
            features=features,
        )

    def _register_extraction_functions(self) -> None:
        """Register advanced L6-specific feature extraction functions."""
        self.register_extraction_function("behavioral_deviation", self._extract_behavioral_deviation)
        self.register_extraction_function("system_metric_anomaly", self._extract_system_metric_anomaly)
        self.register_extraction_function("temporal_pattern_break", self._extract_temporal_pattern_break)
        self.register_extraction_function("reconstruction_error", self._extract_reconstruction_error)
        self.register_extraction_function("multivariate_anomaly", self._extract_multivariate_anomaly)
        self.register_extraction_function("contextual_anomaly", self._extract_contextual_anomaly)
        self.register_extraction_function("performance_degradation", self._extract_performance_degradation)
        self.register_extraction_function("resource_anomaly", self._extract_resource_anomaly)
        self.register_extraction_function("security_anomaly", self._extract_security_anomaly)
        self.register_extraction_function("anomaly_confidence", self._extract_anomaly_confidence)

    def _extract_behavioral_deviation(self, context: dict[str, Any]) -> float:
        """Extract behavioral deviation score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct behavioral deviation if provided
        if "behavioral_deviation" in anomaly:
            return float(anomaly["behavioral_deviation"])

        # Calculate from behavioral patterns
        behavioral_data = anomaly.get("behavioral_data", {})

        if not behavioral_data:
            return 0.0  # Default if no behavioral data

        # Current behavior vs baseline
        current_behavior = behavioral_data.get("current_behavior", {})
        baseline_behavior = behavioral_data.get("baseline_behavior", {})

        if not current_behavior or not baseline_behavior:
            return 0.0

        # Calculate deviation across multiple dimensions
        deviation_factors = {
            "request_frequency": 0.25,
            "response_patterns": 0.2,
            "error_patterns": 0.2,
            "resource_usage": 0.15,
            "timing_patterns": 0.1,
            "interaction_patterns": 0.1,
        }

        total_deviation = 0.0

        # Request frequency deviation
        current_freq = current_behavior.get("request_frequency", 100)
        baseline_freq = baseline_behavior.get("request_frequency", 100)

        if baseline_freq > 0:
            freq_deviation = abs(current_freq - baseline_freq) / baseline_freq
            freq_deviation = min(1.0, freq_deviation)  # Cap at 1.0
        else:
            freq_deviation = 0.0

        total_deviation += deviation_factors["request_frequency"] * freq_deviation

        # Response patterns deviation
        current_response = current_behavior.get("response_patterns", 0.5)
        baseline_response = baseline_behavior.get("response_patterns", 0.5)
        response_deviation = abs(current_response - baseline_response)
        total_deviation += deviation_factors["response_patterns"] * response_deviation

        # Error patterns deviation
        current_errors = current_behavior.get("error_patterns", 0.01)
        baseline_errors = baseline_behavior.get("error_patterns", 0.01)

        if baseline_errors > 0:
            error_deviation = abs(current_errors - baseline_errors) / baseline_errors
            error_deviation = min(1.0, error_deviation)
        else:
            error_deviation = 0.0

        total_deviation += deviation_factors["error_patterns"] * error_deviation

        # Resource usage deviation
        current_resources = current_behavior.get("resource_usage", 0.5)
        baseline_resources = baseline_behavior.get("resource_usage", 0.5)
        resource_deviation = abs(current_resources - baseline_resources)
        total_deviation += deviation_factors["resource_usage"] * resource_deviation

        # Timing patterns deviation
        current_timing = current_behavior.get("timing_patterns", 0.5)
        baseline_timing = baseline_behavior.get("timing_patterns", 0.5)
        timing_deviation = abs(current_timing - baseline_timing)
        total_deviation += deviation_factors["timing_patterns"] * timing_deviation

        # Interaction patterns deviation
        current_interaction = current_behavior.get("interaction_patterns", 0.5)
        baseline_interaction = baseline_behavior.get("interaction_patterns", 0.5)
        interaction_deviation = abs(current_interaction - baseline_interaction)
        total_deviation += deviation_factors["interaction_patterns"] * interaction_deviation

        return round(min(1.0, total_deviation), 3)

    def _extract_system_metric_anomaly(self, context: dict[str, Any]) -> float:
        """Extract system metric anomaly score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct system metric anomaly if provided
        if "system_metric_anomaly" in anomaly:
            return float(anomaly["system_metric_anomaly"])

        # Calculate from system metrics
        system_metrics = anomaly.get("system_metrics", {})

        if not system_metrics:
            return 0.0  # Default if no system metrics

        metric_anomalies = {
            "cpu_anomaly": 0.25,
            "memory_anomaly": 0.25,
            "disk_anomaly": 0.2,
            "network_anomaly": 0.15,
            "process_anomaly": 0.15,
        }

        total_anomaly = 0.0

        # CPU anomaly
        cpu_current = system_metrics.get("cpu_usage", 50)
        cpu_baseline = system_metrics.get("cpu_baseline", 50)
        cpu_threshold = system_metrics.get("cpu_threshold", 80)

        cpu_anomaly_score = 0.0
        if cpu_current > cpu_threshold:
            cpu_anomaly_score = (cpu_current - cpu_threshold) / (100 - cpu_threshold)
        elif abs(cpu_current - cpu_baseline) > 20:  # Significant deviation from baseline
            cpu_anomaly_score = abs(cpu_current - cpu_baseline) / 100

        total_anomaly += metric_anomalies["cpu_anomaly"] * min(1.0, cpu_anomaly_score)

        # Memory anomaly
        memory_current = system_metrics.get("memory_usage", 50)
        memory_baseline = system_metrics.get("memory_baseline", 50)
        memory_threshold = system_metrics.get("memory_threshold", 85)

        memory_anomaly_score = 0.0
        if memory_current > memory_threshold:
            memory_anomaly_score = (memory_current - memory_threshold) / (100 - memory_threshold)
        elif abs(memory_current - memory_baseline) > 15:
            memory_anomaly_score = abs(memory_current - memory_baseline) / 100

        total_anomaly += metric_anomalies["memory_anomaly"] * min(1.0, memory_anomaly_score)

        # Disk anomaly
        disk_io = system_metrics.get("disk_io", 50)
        disk_baseline = system_metrics.get("disk_baseline", 50)
        disk_anomaly_score = abs(disk_io - disk_baseline) / 100
        total_anomaly += metric_anomalies["disk_anomaly"] * min(1.0, disk_anomaly_score)

        # Network anomaly
        network_io = system_metrics.get("network_io", 50)
        network_baseline = system_metrics.get("network_baseline", 50)
        network_anomaly_score = abs(network_io - network_baseline) / 100
        total_anomaly += metric_anomalies["network_anomaly"] * min(1.0, network_anomaly_score)

        # Process anomaly
        process_count = system_metrics.get("process_count", 100)
        process_baseline = system_metrics.get("process_baseline", 100)
        process_anomaly_score = abs(process_count - process_baseline) / max(1, process_baseline)
        total_anomaly += metric_anomalies["process_anomaly"] * min(1.0, process_anomaly_score)

        return round(min(1.0, total_anomaly), 3)

    def _extract_temporal_pattern_break(self, context: dict[str, Any]) -> float:
        """Extract temporal pattern break score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct temporal pattern break if provided
        if "temporal_pattern_break" in anomaly:
            return float(anomaly["temporal_pattern_break"])

        # Calculate from temporal patterns
        temporal_data = anomaly.get("temporal_data", {})

        if not temporal_data:
            return 0.0  # Default if no temporal data

        pattern_breaks = {
            "hourly_pattern": 0.3,
            "daily_pattern": 0.25,
            "weekly_pattern": 0.2,
            "seasonal_pattern": 0.15,
            "trend_deviation": 0.1,
        }

        total_break = 0.0

        # Hourly pattern break
        current_hour = datetime.now().hour
        hourly_pattern = temporal_data.get("hourly_pattern", {})
        expected_hourly = hourly_pattern.get(str(current_hour), 0.1)
        actual_hourly = temporal_data.get("current_hourly_activity", 0.1)

        if expected_hourly > 0:
            hourly_break = abs(actual_hourly - expected_hourly) / expected_hourly
            total_break += pattern_breaks["hourly_pattern"] * min(1.0, hourly_break)

        # Daily pattern break
        current_day = datetime.now().weekday()
        daily_pattern = temporal_data.get("daily_pattern", {})
        expected_daily = daily_pattern.get(str(current_day), 0.14)  # 1/7 baseline
        actual_daily = temporal_data.get("current_daily_activity", 0.14)

        if expected_daily > 0:
            daily_break = abs(actual_daily - expected_daily) / expected_daily
            total_break += pattern_breaks["daily_pattern"] * min(1.0, daily_break)

        # Weekly pattern break
        weekly_trend = temporal_data.get("weekly_trend", [])
        if len(weekly_trend) >= 4:
            recent_avg = sum(weekly_trend[-2:]) / 2
            older_avg = sum(weekly_trend[-4:-2]) / 2

            if older_avg > 0:
                weekly_break = abs(recent_avg - older_avg) / older_avg
                total_break += pattern_breaks["weekly_pattern"] * min(1.0, weekly_break)

        # Seasonal pattern break
        seasonal_data = temporal_data.get("seasonal_data", {})
        current_season = datetime.now().month // 3  # 0-3 for seasons
        expected_seasonal = seasonal_data.get(str(current_season), 0.25)
        actual_seasonal = temporal_data.get("current_seasonal_activity", 0.25)

        if expected_seasonal > 0:
            seasonal_break = abs(actual_seasonal - expected_seasonal) / expected_seasonal
            total_break += pattern_breaks["seasonal_pattern"] * min(1.0, seasonal_break)

        # Trend deviation
        trend_data = temporal_data.get("trend_data", [])
        if len(trend_data) >= 10:
            # Calculate trend deviation
            recent_trend = trend_data[-5:]
            older_trend = trend_data[-10:-5]

            recent_avg = sum(recent_trend) / len(recent_trend)
            older_avg = sum(older_trend) / len(older_trend)

            if older_avg > 0:
                trend_break = abs(recent_avg - older_avg) / older_avg
                total_break += pattern_breaks["trend_deviation"] * min(1.0, trend_break)

        return round(min(1.0, total_break), 3)

    def _extract_reconstruction_error(self, context: dict[str, Any]) -> float:
        """Extract reconstruction error score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct reconstruction error if provided
        if "reconstruction_error" in anomaly:
            return float(anomaly["reconstruction_error"])

        # Calculate from autoencoder data
        autoencoder_data = anomaly.get("autoencoder_data", {})

        if not autoencoder_data:
            return 0.0  # Default if no autoencoder data

        # Reconstruction error components
        reconstruction_components = {
            "input_reconstruction": 0.4,
            "latent_reconstruction": 0.3,
            "output_reconstruction": 0.3,
        }

        total_error = 0.0

        # Input reconstruction error
        input_error = autoencoder_data.get("input_reconstruction_error", 0.0)
        input_threshold = autoencoder_data.get("input_error_threshold", 0.1)

        if input_threshold > 0:
            input_error_score = min(1.0, input_error / input_threshold)
        else:
            input_error_score = 0.0

        total_error += reconstruction_components["input_reconstruction"] * input_error_score

        # Latent reconstruction error
        latent_error = autoencoder_data.get("latent_reconstruction_error", 0.0)
        latent_threshold = autoencoder_data.get("latent_error_threshold", 0.1)

        if latent_threshold > 0:
            latent_error_score = min(1.0, latent_error / latent_threshold)
        else:
            latent_error_score = 0.0

        total_error += reconstruction_components["latent_reconstruction"] * latent_error_score

        # Output reconstruction error
        output_error = autoencoder_data.get("output_reconstruction_error", 0.0)
        output_threshold = autoencoder_data.get("output_error_threshold", 0.1)

        if output_threshold > 0:
            output_error_score = min(1.0, output_error / output_threshold)
        else:
            output_error_score = 0.0

        total_error += reconstruction_components["output_reconstruction"] * output_error_score

        return round(min(1.0, total_error), 3)

    def _extract_multivariate_anomaly(self, context: dict[str, Any]) -> float:
        """Extract multivariate anomaly score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct multivariate anomaly if provided
        if "multivariate_anomaly" in anomaly:
            return float(anomaly["multivariate_anomaly"])

        # Calculate from multivariate analysis
        multivariate_data = anomaly.get("multivariate_data", {})

        if not multivariate_data:
            return 0.0  # Default if no multivariate data

        # Multivariate anomaly components
        multivariate_components = {
            "correlation_anomaly": 0.3,
            "covariance_anomaly": 0.25,
            "distribution_anomaly": 0.25,
            "dimension_anomaly": 0.2,
        }

        total_anomaly = 0.0

        # Correlation anomaly
        correlation_deviation = multivariate_data.get("correlation_deviation", 0.0)
        correlation_threshold = multivariate_data.get("correlation_threshold", 0.5)

        if correlation_threshold > 0:
            correlation_anomaly = min(1.0, correlation_deviation / correlation_threshold)
        else:
            correlation_anomaly = 0.0

        total_anomaly += multivariate_components["correlation_anomaly"] * correlation_anomaly

        # Covariance anomaly
        covariance_deviation = multivariate_data.get("covariance_deviation", 0.0)
        covariance_threshold = multivariate_data.get("covariance_threshold", 0.5)

        if covariance_threshold > 0:
            covariance_anomaly = min(1.0, covariance_deviation / covariance_threshold)
        else:
            covariance_anomaly = 0.0

        total_anomaly += multivariate_components["covariance_anomaly"] * covariance_anomaly

        # Distribution anomaly
        distribution_deviation = multivariate_data.get("distribution_deviation", 0.0)
        distribution_threshold = multivariate_data.get("distribution_threshold", 0.5)

        if distribution_threshold > 0:
            distribution_anomaly = min(1.0, distribution_deviation / distribution_threshold)
        else:
            distribution_anomaly = 0.0

        total_anomaly += multivariate_components["distribution_anomaly"] * distribution_anomaly

        # Dimension anomaly
        dimension_deviation = multivariate_data.get("dimension_deviation", 0.0)
        dimension_threshold = multivariate_data.get("dimension_threshold", 0.5)

        if dimension_threshold > 0:
            dimension_anomaly = min(1.0, dimension_deviation / dimension_threshold)
        else:
            dimension_anomaly = 0.0

        total_anomaly += multivariate_components["dimension_anomaly"] * dimension_anomaly

        return round(min(1.0, total_anomaly), 3)

    def _extract_contextual_anomaly(self, context: dict[str, Any]) -> float:
        """Extract contextual anomaly score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct contextual anomaly if provided
        if "contextual_anomaly" in anomaly:
            return float(anomaly["contextual_anomaly"])

        # Calculate from contextual factors
        contextual_data = anomaly.get("contextual_data", {})

        if not contextual_data:
            return 0.0  # Default if no contextual data

        # Contextual anomaly components
        contextual_components = {
            "environmental_anomaly": 0.3,
            "user_context_anomaly": 0.25,
            "system_context_anomaly": 0.25,
            "temporal_context_anomaly": 0.2,
        }

        total_anomaly = 0.0

        # Environmental anomaly
        environmental_deviation = contextual_data.get("environmental_deviation", 0.0)
        environmental_anomaly = min(1.0, environmental_deviation)
        total_anomaly += contextual_components["environmental_anomaly"] * environmental_anomaly

        # User context anomaly
        user_deviation = contextual_data.get("user_context_deviation", 0.0)
        user_anomaly = min(1.0, user_deviation)
        total_anomaly += contextual_components["user_context_anomaly"] * user_anomaly

        # System context anomaly
        system_deviation = contextual_data.get("system_context_deviation", 0.0)
        system_anomaly = min(1.0, system_deviation)
        total_anomaly += contextual_components["system_context_anomaly"] * system_anomaly

        # Temporal context anomaly
        temporal_deviation = contextual_data.get("temporal_context_deviation", 0.0)
        temporal_anomaly = min(1.0, temporal_deviation)
        total_anomaly += contextual_components["temporal_context_anomaly"] * temporal_anomaly

        return round(min(1.0, total_anomaly), 3)

    def _extract_performance_degradation(self, context: dict[str, Any]) -> float:
        """Extract performance degradation score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct performance degradation if provided
        if "performance_degradation" in anomaly:
            return float(anomaly["performance_degradation"])

        # Calculate from performance metrics
        performance_data = anomaly.get("performance_data", {})

        if not performance_data:
            return 0.0  # Default if no performance data

        # Performance degradation components
        performance_components = {
            "response_time_degradation": 0.3,
            "throughput_degradation": 0.25,
            "error_rate_increase": 0.25,
            "latency_increase": 0.2,
        }

        total_degradation = 0.0

        # Response time degradation
        current_response_time = performance_data.get("current_response_time", 100)
        baseline_response_time = performance_data.get("baseline_response_time", 100)

        if baseline_response_time > 0:
            response_degradation = (
                max(0, (current_response_time - baseline_response_time)) / baseline_response_time
            )
            response_degradation = min(1.0, response_degradation)
        else:
            response_degradation = 0.0

        total_degradation += performance_components["response_time_degradation"] * response_degradation

        # Throughput degradation
        current_throughput = performance_data.get("current_throughput", 100)
        baseline_throughput = performance_data.get("baseline_throughput", 100)

        if baseline_throughput > 0:
            throughput_degradation = max(0, (baseline_throughput - current_throughput)) / baseline_throughput
            throughput_degradation = min(1.0, throughput_degradation)
        else:
            throughput_degradation = 0.0

        total_degradation += performance_components["throughput_degradation"] * throughput_degradation

        # Error rate increase
        current_error_rate = performance_data.get("current_error_rate", 0.01)
        baseline_error_rate = performance_data.get("baseline_error_rate", 0.01)

        if baseline_error_rate > 0:
            error_increase = max(0, (current_error_rate - baseline_error_rate)) / baseline_error_rate
            error_increase = min(1.0, error_increase)
        else:
            error_increase = 0.0

        total_degradation += performance_components["error_rate_increase"] * error_increase

        # Latency increase
        current_latency = performance_data.get("current_latency", 50)
        baseline_latency = performance_data.get("baseline_latency", 50)

        if baseline_latency > 0:
            latency_increase = max(0, (current_latency - baseline_latency)) / baseline_latency
            latency_increase = min(1.0, latency_increase)
        else:
            latency_increase = 0.0

        total_degradation += performance_components["latency_increase"] * latency_increase

        return round(min(1.0, total_degradation), 3)

    def _extract_resource_anomaly(self, context: dict[str, Any]) -> float:
        """Extract resource anomaly score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct resource anomaly if provided
        if "resource_anomaly" in anomaly:
            return float(anomaly["resource_anomaly"])

        # Calculate from resource metrics
        resource_data = anomaly.get("resource_data", {})

        if not resource_data:
            return 0.0  # Default if no resource data

        # Resource anomaly components
        resource_components = {
            "memory_anomaly": 0.3,
            "cpu_anomaly": 0.3,
            "disk_anomaly": 0.2,
            "network_anomaly": 0.2,
        }

        total_anomaly = 0.0

        # Memory anomaly
        memory_usage = resource_data.get("memory_usage", 50)
        memory_threshold = resource_data.get("memory_threshold", 85)

        if memory_usage > memory_threshold:
            memory_anomaly = (memory_usage - memory_threshold) / (100 - memory_threshold)
        else:
            memory_anomaly = 0.0

        total_anomaly += resource_components["memory_anomaly"] * min(1.0, memory_anomaly)

        # CPU anomaly
        cpu_usage = resource_data.get("cpu_usage", 50)
        cpu_threshold = resource_data.get("cpu_threshold", 80)

        if cpu_usage > cpu_threshold:
            cpu_anomaly = (cpu_usage - cpu_threshold) / (100 - cpu_threshold)
        else:
            cpu_anomaly = 0.0

        total_anomaly += resource_components["cpu_anomaly"] * min(1.0, cpu_anomaly)

        # Disk anomaly
        disk_usage = resource_data.get("disk_usage", 50)
        disk_threshold = resource_data.get("disk_threshold", 90)

        if disk_usage > disk_threshold:
            disk_anomaly = (disk_usage - disk_threshold) / (100 - disk_threshold)
        else:
            disk_anomaly = 0.0

        total_anomaly += resource_components["disk_anomaly"] * min(1.0, disk_anomaly)

        # Network anomaly
        network_usage = resource_data.get("network_usage", 50)
        network_threshold = resource_data.get("network_threshold", 85)

        if network_usage > network_threshold:
            network_anomaly = (network_usage - network_threshold) / (100 - network_threshold)
        else:
            network_anomaly = 0.0

        total_anomaly += resource_components["network_anomaly"] * min(1.0, network_anomaly)

        return round(min(1.0, total_anomaly), 3)

    def _extract_security_anomaly(self, context: dict[str, Any]) -> float:
        """Extract security anomaly score (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct security anomaly if provided
        if "security_anomaly" in anomaly:
            return float(anomaly["security_anomaly"])

        # Calculate from security indicators
        security_data = anomaly.get("security_data", {})

        if not security_data:
            return 0.0  # Default if no security data

        # Security anomaly components
        security_components = {
            "authentication_anomaly": 0.3,
            "authorization_anomaly": 0.25,
            "access_pattern_anomaly": 0.25,
            "threat_indicators": 0.2,
        }

        total_anomaly = 0.0

        # Authentication anomaly
        auth_failures = security_data.get("authentication_failures", 0)
        auth_threshold = security_data.get("auth_failure_threshold", 5)

        if auth_failures > auth_threshold:
            auth_anomaly = min(1.0, (auth_failures - auth_threshold) / auth_threshold)
        else:
            auth_anomaly = 0.0

        total_anomaly += security_components["authentication_anomaly"] * auth_anomaly

        # Authorization anomaly
        unauthorized_attempts = security_data.get("unauthorized_attempts", 0)
        authz_threshold = security_data.get("unauthorized_threshold", 3)

        if unauthorized_attempts > authz_threshold:
            authz_anomaly = min(1.0, (unauthorized_attempts - authz_threshold) / authz_threshold)
        else:
            authz_anomaly = 0.0

        total_anomaly += security_components["authorization_anomaly"] * authz_anomaly

        # Access pattern anomaly
        access_deviation = security_data.get("access_pattern_deviation", 0.0)
        access_anomaly = min(1.0, access_deviation)
        total_anomaly += security_components["access_pattern_anomaly"] * access_anomaly

        # Threat indicators
        threat_score = security_data.get("threat_score", 0.0)
        threat_anomaly = min(1.0, threat_score)
        total_anomaly += security_components["threat_indicators"] * threat_anomaly

        return round(min(1.0, total_anomaly), 3)

    def _extract_anomaly_confidence(self, context: dict[str, Any]) -> float:
        """Extract overall anomaly confidence (0.0 to 1.0)."""
        anomaly = context.get("anomaly", {})

        # Direct anomaly confidence if provided
        if "anomaly_confidence" in anomaly:
            return float(anomaly["anomaly_confidence"])

        # Calculate from individual anomaly factors
        confidence_factors = {
            "behavioral_deviation": 0.15,
            "system_metric_anomaly": 0.15,
            "temporal_pattern_break": 0.1,
            "reconstruction_error": 0.2,
            "multivariate_anomaly": 0.15,
            "contextual_anomaly": 0.1,
            "performance_degradation": 0.05,
            "resource_anomaly": 0.05,
            "security_anomaly": 0.05,
        }

        # Extract individual anomaly scores
        behavioral_score = self._extract_behavioral_deviation(context)
        system_score = self._extract_system_metric_anomaly(context)
        temporal_score = self._extract_temporal_pattern_break(context)
        reconstruction_score = self._extract_reconstruction_error(context)
        multivariate_score = self._extract_multivariate_anomaly(context)
        contextual_score = self._extract_contextual_anomaly(context)
        performance_score = self._extract_performance_degradation(context)
        resource_score = self._extract_resource_anomaly(context)
        security_score = self._extract_security_anomaly(context)

        # Weighted combination
        anomaly_confidence = (
            confidence_factors["behavioral_deviation"] * behavioral_score
            + confidence_factors["system_metric_anomaly"] * system_score
            + confidence_factors["temporal_pattern_break"] * temporal_score
            + confidence_factors["reconstruction_error"] * reconstruction_score
            + confidence_factors["multivariate_anomaly"] * multivariate_score
            + confidence_factors["contextual_anomaly"] * contextual_score
            + confidence_factors["performance_degradation"] * performance_score
            + confidence_factors["resource_anomaly"] * resource_score
            + confidence_factors["security_anomaly"] * security_score
        )

        return round(max(0.0, min(1.0, anomaly_confidence)), 3)
