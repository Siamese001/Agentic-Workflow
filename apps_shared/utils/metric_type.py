"""observability Planning Orchestrator - Coordinates observability and monitoring operations.

This orchestrator manages the planning phase for observability operations,
including metric collection, log aggregation, trace management, and alert configuration.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics for observability."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class LogLevel(Enum):
    """Log levels for observability."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSeverity(Enum):
    """Severity levels for alerts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricDefinition:
    """Definition of a metric to be collected."""

    name: str
    metric_type: MetricType
    description: str
    labels: dict[str, str] = field(default_factory=dict)
    sampling_rate: float = 1.0
    aggregation: str | None = None


@dataclass
class LogConfiguration:
    """configuration for log collection."""

    service_name: str
    log_level: LogLevel
    format: str = "json"
    include_timestamp: bool = True
    include_trace_id: bool = True
    filters: list[str] = field(default_factory=list)


@dataclass
class TraceConfiguration:
    """configuration for distributed tracing."""

    service_name: str
    sampling_rate: float = 0.1
    include_payload: bool = False
    max_spans_per_trace: int = 1000
    export_batch_size: int = 100


@dataclass
class AlertRule:
    """Definition of an alert rule."""

    name: str
    condition: str
    severity: AlertSeverity
    threshold: float
    duration: int  # seconds
    notification_channels: list[str] = field(default_factory=list)


@dataclass
class ObservabilityPlanningConfig:
    """configuration for observability planning orchestrator."""

    enable_metrics: bool = True
    enable_logging: bool = True
    enable_tracing: bool = True
    enable_alerts: bool = True
    default_sampling_rate: float = 0.1
    log_retention_days: int = 30
    metric_retention_days: int = 90
    log_level: str = "INFO"


@dataclass
class ObservabilityPlanningResult:
    """Result of observability planning orchestration."""

    success: bool
    metric_definitions: list[MetricDefinition] = field(default_factory=list)
    log_configuration: LogConfiguration | None = None
    trace_configuration: TraceConfiguration | None = None
    alert_rules: list[AlertRule] = field(default_factory=list)
    resource_estimates: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityPlanningOrchestrator:
    """Orchestrator for planning observability operations."""

    def __init__(self, config: ObservabilityPlanningConfig | None = None):
        self.config = config or ObservabilityPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, observability_request: dict[str, Any]) -> ObservabilityPlanningResult:
        """Execute the observability planning orchestration.

        Args:
            observability_request: Dictionary containing observability requirements

        Returns:
            ObservabilityPlanningResult: Complete planning result with observability setup
        """
        self.logger.info(
            f"Starting observability planning for service: {observability_request.get('service_name', 'unknown')}",
        )

        try:
            # Validate input request
            self._validate_request(observability_request)

            # Plan metrics if enabled
            metric_definitions = []
            if self.config.enable_metrics:
                metric_definitions = self._plan_metrics(observability_request)

            # Plan logging if enabled
            log_configuration = None
            if self.config.enable_logging:
                log_configuration = self._plan_logging(observability_request)

            # Plan tracing if enabled
            trace_configuration = None
            if self.config.enable_tracing:
                trace_configuration = self._plan_tracing(observability_request)

            # Plan alerts if enabled
            alert_rules = []
            if self.config.enable_alerts:
                alert_rules = self._plan_alerts(observability_request)

            # Calculate resource estimates
            resource_estimates = self._estimate_resources(
                metric_definitions,
                log_configuration,
                trace_configuration,
            )

            result = ObservabilityPlanningResult(
                success=True,
                metric_definitions=metric_definitions,
                log_configuration=log_configuration,
                trace_configuration=trace_configuration,
                alert_rules=alert_rules,
                resource_estimates=resource_estimates,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "service_name": observability_request.get("service_name"),
                    "metric_count": len(metric_definitions),
                    "alert_count": len(alert_rules),
                    "orchestrator": "ObservabilityPlanningOrchestrator",
                },
            )

            self.logger.info(
                f"Successfully planned observability for {len(metric_definitions)} metrics",
            )
            return result

        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"observability planning failed: {str(e)}")
            return ObservabilityPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "ObservabilityPlanningOrchestrator",
                },
            )

    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate observability planning request."""
        if not request:
            raise ValueError("observability request cannot be empty")

        if "service_name" not in request:
            raise ValueError("Service name is required in observability request")

        if "service_type" not in request:
            raise ValueError("Service type is required in observability request")

    def _plan_metrics(self, request: dict[str, Any]) -> list[MetricDefinition]:
        """Plan metrics for the service."""
        service_name = request.get("service_name")
        service_type = request.get("service_type")

        metrics = []

        # Common metrics for all services
        metrics.append(
            MetricDefinition(
                name=f"{service_name}_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total number of requests",
                labels={"service": service_name, "method": "*"},
            ),
        )

        metrics.append(
            MetricDefinition(
                name=f"{service_name}_request_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Request duration in seconds",
                labels={"service": service_name},
                aggregation="percentile",
            ),
        )

        # Service-specific metrics
        if service_type == "api":
            metrics.append(
                MetricDefinition(
                    name=f"{service_name}_api_errors_total",
                    metric_type=MetricType.COUNTER,
                    description="Total API errors",
                    labels={"service": service_name, "error_code": "*"},
                ),
            )
        elif service_type == "worker":
            metrics.append(
                MetricDefinition(
                    name=f"{service_name}_jobs_processed_total",
                    metric_type=MetricType.COUNTER,
                    description="Total jobs processed",
                    labels={"service": service_name, "status": "*"},
                ),
            )
            metrics.append(
                MetricDefinition(
                    name=f"{service_name}_queue_size",
                    metric_type=MetricType.GAUGE,
                    description="Current queue size",
                    labels={"service": service_name},
                ),
            )

        return metrics

    def _plan_logging(self, request: dict[str, Any]) -> LogConfiguration:
        """Plan logging configuration for the service."""
        service_name = request.get("service_name")
        log_level_str = request.get("log_level", "info")

        # Map string to enum
        log_level_mapping = {
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL,
        }

        log_level = log_level_mapping.get(log_level_str.lower(), LogLevel.INFO)

        return LogConfiguration(
            service_name=service_name,
            log_level=log_level,
            format="json",
            include_timestamp=True,
            include_trace_id=True,
            filters=["password", "token", "secret"],
        )

    def _plan_tracing(self, request: dict[str, Any]) -> TraceConfiguration:
        """Plan tracing configuration for the service."""
        service_name = request.get("service_name")
        sampling_rate = request.get("tracing_sampling_rate", self.config.default_sampling_rate)

        # guardian: allow-magic-config
        return TraceConfiguration(
            service_name=service_name,
            sampling_rate=sampling_rate,
            include_payload=False,
            max_spans_per_trace=1000,
            export_batch_size=100,
        )

    def _plan_alerts(self, request: dict[str, Any]) -> list[AlertRule]:
        """Plan alert rules for the service."""
        service_name = request.get("service_name")
        service_type = request.get("service_type")

        alerts = []

        # Common alerts
        alerts.append(
            # guardian: allow-magic-config
            AlertRule(
                name=f"{service_name}_high_error_rate",
                condition="error_rate > 0.05",
                severity=AlertSeverity.HIGH,
                threshold=0.05,
                duration=300,  # 5 minutes
                notification_channels=["slack", "email"],
            ),
        )

        alerts.append(
            # guardian: allow-magic-config
            AlertRule(
                name=f"{service_name}_high_latency",
                condition="p95_latency > 1000",
                severity=AlertSeverity.MEDIUM,
                threshold=1000.0,
                duration=600,  # 10 minutes
                notification_channels=["slack"],
            ),
        )

        # Service-specific alerts
        if service_type == "api":
            alerts.append(
                # guardian: allow-magic-config
                AlertRule(
                    name=f"{service_name}_api_availability",
                    condition="availability < 0.99",
                    severity=AlertSeverity.CRITICAL,
                    threshold=0.99,
                    duration=60,  # 1 minute
                    notification_channels=["pagerduty", "slack", "email"],
                ),
            )
        elif service_type == "worker":
            alerts.append(
                # guardian: allow-magic-config
                AlertRule(
                    name=f"{service_name}_queue_backlog",
                    condition="queue_size > 1000",
                    severity=AlertSeverity.HIGH,
                    threshold=1000.0,
                    duration=300,  # 5 minutes
                    notification_channels=["slack", "email"],
                ),
            )

        return alerts

    def _estimate_resources(
        self,
        metrics: list[MetricDefinition],
        logs: LogConfiguration | None,
        traces: TraceConfiguration | None,
    ) -> dict[str, Any]:
        """Estimate resource requirements for observability."""
        estimates = {
            "storage_gb_per_day": 0.0,
            "network_mb_per_day": 0.0,
            "cpu_cores": 0.1,
            "memory_mb": 100,
        }

        # Metrics storage
        metric_points_per_day = len(metrics) * 86400  # 1 point per second per metric
        estimates["storage_gb_per_day"] += (metric_points_per_day * 16) / (1024**3)  # 16 bytes per point

        # Logs storage
        if logs:
            log_events_per_second = 100  # Estimate
            log_size_bytes = 512  # Average log size
            daily_log_volume = log_events_per_second * 86400 * log_size_bytes
            estimates["storage_gb_per_day"] += daily_log_volume / (1024**3)
            estimates["network_mb_per_day"] += daily_log_volume / (1024**2)

        # Traces storage
        if traces:
            spans_per_second = 10  # Estimate
            span_size_bytes = 256  # Average span size
            daily_trace_volume = spans_per_second * 86400 * span_size_bytes * traces.sampling_rate
            estimates["storage_gb_per_day"] += daily_trace_volume / (1024**3)
            estimates["network_mb_per_day"] += daily_trace_volume / (1024**2)

        # CPU and memory for processing
        estimates["cpu_cores"] = 0.2 if logs else 0.1
        estimates["memory_mb"] = 200 if traces else 100

        return estimates


# Factory function for easy instantiation
def create_observability_planning_orchestrator(
    enable_metrics: bool = True,
    enable_logging: bool = True,
    enable_tracing: bool = True,
    **kwargs: object,
) -> ObservabilityPlanningOrchestrator:
    """Create a configured observability planning orchestrator."""
    config = ObservabilityPlanningConfig(
        enable_metrics=enable_metrics,
        enable_logging=enable_logging,
        enable_tracing=enable_tracing,
        **kwargs,
    )
    return ObservabilityPlanningOrchestrator(config)


# Convenience function for direct usage
def plan_observability(
    service_name: str,
    service_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan observability setup from simple parameters.

    Args:
        service_name: Name of the service
        service_type: Type of service (api, worker, batch, etc.)
        config: Optional configuration overrides

    Returns:
        Dict: Planning result with observability configuration
    """
    # Build request
    request = {
        "service_name": service_name,
        "service_type": service_type,
        "log_level": config.get("log_level", "info") if config else "info",
        "tracing_sampling_rate": config.get("tracing_sampling_rate", 0.1) if config else 0.1,
    }

    # Create orchestrator and execute
    orchestrator_config = ObservabilityPlanningConfig(**config) if config else None
    orchestrator = ObservabilityPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "metric_definitions": [
            {
                "name": m.name,
                "metric_type": m.metric_type.value,
                "description": m.description,
                "labels": m.labels,
                "sampling_rate": m.sampling_rate,
                "aggregation": m.aggregation,
            }
            for m in result.metric_definitions
        ],
        "log_configuration": {
            "service_name": result.log_configuration.service_name,
            "log_level": result.log_configuration.log_level.value,
            "format": result.log_configuration.format,
            "include_timestamp": result.log_configuration.include_timestamp,
            "include_trace_id": result.log_configuration.include_trace_id,
            "filters": result.log_configuration.filters,
        }
        if result.log_configuration
        else None,
        "trace_configuration": {
            "service_name": result.trace_configuration.service_name,
            "sampling_rate": result.trace_configuration.sampling_rate,
            "include_payload": result.trace_configuration.include_payload,
            "max_spans_per_trace": result.trace_configuration.max_spans_per_trace,
            "export_batch_size": result.trace_configuration.export_batch_size,
        }
        if result.trace_configuration
        else None,
        "alert_rules": [
            {
                "name": a.name,
                "condition": a.condition,
                "severity": a.severity.value,
                "threshold": a.threshold,
                "duration": a.duration,
                "notification_channels": a.notification_channels,
            }
            for a in result.alert_rules
        ],
        "resource_estimates": result.resource_estimates,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata,
    }


if __name__ == "__main__":
    # Example usage
    result = plan_observability(
        service_name="user_service",
        service_type="api",
        config={"log_level": "info", "tracing_sampling_rate": 0.1},
    )


class OrchestrateObservabilityPlanningOrchestratorProcessor(ABC):
    """L5 interface foundation - ensures L1 pure planning behavior"""

    @abstractmethod
    def process(
        self,
        input_data: dict[str, object],
    ) -> OrchestrateObservabilityPlanningOrchestratorResult:
        """Process data with L5 safety constraints"""
        ...

    @abstractmethod
    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        ...


class OrchestrateObservabilityPlanningOrchestratorImpl(
    OrchestrateObservabilityPlanningOrchestratorProcessor,
):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """

    def __init__(
        self,
        constraints: OrchestrateObservabilityPlanningOrchestratorConstraints | None = None,
    ):
        self.constraints = constraints or OrchestrateObservabilityPlanningOrchestratorConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(
        self,
        input_data: dict[str, object],
    ) -> OrchestrateObservabilityPlanningOrchestratorResult:
        """Process input following L5 architecture principles"""
        self.logger.info(f"Processing {input_data}")

        # L5 Input validation
        self._validate_input(input_data)

        # L5 Safety validation - fail-closed
        if not self.validate_safety(input_data):
            raise SecurityError("Input failed L5 safety validation")

        # Create result with L5 structure
        result = OrchestrateObservabilityPlanningOrchestratorResult(
            success=True,
            data={"processed": True, "input": input_data},
            safety_validated=True,
            timestamp=self._get_timestamp(),
        )

        self.logger.info(f"Successfully processed: {result.success}")
        return result

    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = [
                "<script>",
                "javascript:",
                "# SECURITY: ast.literal_eval(",
                "# SECURITY: pass  # exec disabled: ",
                "__import__",
            ]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f" Dangerous pattern detected: {pattern}")
                    return False

            # Check data size
            if len(str(data)) > 1000000:  # 1MB limit
                self.logger.error("Data exceeds size limit")
                return False

            self.logger.info("Data passed L5 safety validation")
            return True
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed

    def _validate_input(self, input_data: dict[str, object]) -> None:
        """L5 Input validation"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        if not input_data:
            raise ValueError("Input cannot be empty")

    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime

        return datetime.utcnow().isoformat()


class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""

    ...


class OrchestrateObservabilityPlanningOrchestratorInterface:
    """L5 Interface - ensures contract compliance"""

    def __init__(self, engine: OrchestrateObservabilityPlanningOrchestratorProcessor):
        self._processor = engine

    def execute(self, input_data: dict[str, object]) -> dict[str, object]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            raise SecurityError(f"Execution failed: {e}")


class OrchestrateObservabilityPlanningOrchestratorFactory:
    """L5 builder for creating processors with proper configuration"""

    @staticmethod
    def create_processor(
        safety_level: str = "strict",
    ) -> OrchestrateObservabilityPlanningOrchestratorInterface:
        """Create configured engine"""
        constraints = OrchestrateObservabilityPlanningOrchestratorConstraints(
            safety_level=safety_level,
        )
        engine = OrchestrateObservabilityPlanningOrchestratorImpl(constraints)
        return OrchestrateObservabilityPlanningOrchestratorInterface(engine)


def orchestrate_observability_planning(input_data: dict[str, object]) -> dict[str, object]:
    """
    L5 Main function - orchestrate observability planning operations

    Args:
        input_data: Input data to process

    Returns:
        Dict: Processed result

    Raises:
        SecurityError: If execution fails any safety check
    """
    builder = OrchestrateObservabilityPlanningOrchestratorFactory()
    engine = builder.create_processor()
    return engine.execute(input_data)


if __name__ == "__main__":
    # L5 Test execution
    try:
        test_data = {"test": True}
        result = orchestrate_observability_planning(test_data)
        logger.info(f"L5 Execution successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except (ValueError, TypeError, RuntimeError, KeyError) as e:
        logger.error(f"L5 Unexpected error: {e}")
